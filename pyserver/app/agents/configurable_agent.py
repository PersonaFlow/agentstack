from enum import Enum
from typing import Any, Mapping, Optional, Sequence
from langchain_core.messages import AnyMessage
from langchain_core.runnables import (
    ConfigurableField,
    ConfigurableFieldMultiOption,
    RunnableBinding,
)
from langgraph.checkpoint import BaseCheckpointSaver
from app.core.pg_checkpoint_saver import get_pg_checkpoint_saver
from app.agents import get_openai_agent_executor, get_chatbot_executor
from app.llms import get_openai_llm
from app.agents.retrieval import get_retrieval_executor
from app.agents.tools import (
    RETRIEVAL_DESCRIPTION,
    TOOL_OPTIONS,
    TOOLS,
    AvailableTools,
    get_retrieval_tool,
    get_retriever,
)
from app.core.configuration import Settings

class AgentType(str, Enum):
    GPT_35_TURBO = "GPT 3.5 Turbo"
    GPT_4 = "GPT 4"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"


DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


def get_agent_executor(
    tools: list,
    agent: AgentType,
    system_message: str,
    interrupt_before_action: bool = False,
    checkpointer: Optional[BaseCheckpointSaver] = None,
):
    if not checkpointer:
        checkpointer = get_pg_checkpoint_saver()
    if agent == AgentType.GPT_35_TURBO:
        llm = get_openai_llm()
        return get_openai_agent_executor(tools, llm, system_message, interrupt_before_action, checkpointer)
    elif agent == AgentType.GPT_4:
        llm = get_openai_llm(gpt_4=True)
        return get_openai_agent_executor(tools, llm, system_message, interrupt_before_action, checkpointer)
    elif agent == AgentType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
        return get_openai_agent_executor(tools, llm, system_message, interrupt_before_action, checkpointer)
    else:
        raise ValueError("Unexpected agent type")

class ConfigurableAgent(RunnableBinding):
    tools: Sequence[str]
    agent: AgentType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    retrieval_description: str = RETRIEVAL_DESCRIPTION
    assistant_id: Optional[str] = None
    interrupt_before_action: bool = False

    def __init__(
        self,
        *,
        tools: Sequence[str],
        agent: AgentType = AgentType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        retrieval_description: str = RETRIEVAL_DESCRIPTION,
        interrupt_before_action: bool = False,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        settings = Settings()
        if not checkpointer:
            checkpointer = get_pg_checkpoint_saver()

        others.pop("bound", None)
        _tools = []
        for _tool in tools:
            if _tool == AvailableTools.RETRIEVAL:
                if assistant_id is None:
                    raise ValueError(
                        "assistant_id must be provided if Retrieval tool is used"
                    )
                _tools.append(get_retrieval_tool(assistant_id, retrieval_description))
            else:
                _returned_tools = TOOLS[_tool]()
                if isinstance(_returned_tools, list):
                    _tools.extend(_returned_tools)
                else:
                    _tools.append(_returned_tools)
        _agent = get_agent_executor(_tools, agent, system_message, interrupt_before_action, checkpointer)
        agent_executor = _agent.with_config({"recursion_limit": settings.LANGGRAPH_RECURSION_LIMIT})
        super().__init__(
            tools=tools,
            agent=agent,
            system_message=system_message,
            retrieval_description=retrieval_description,
            bound=agent_executor,
            kwargs=kwargs or {},
            config=config or {},
        )


class LLMType(str, Enum):
    GPT_35_TURBO = "GPT 3.5 Turbo"
    GPT_4 = "GPT 4"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"

def get_chatbot(
    llm_type: LLMType,
    system_message: str,
    checkpointer: Optional[BaseCheckpointSaver] = None,
):
    if llm_type == LLMType.GPT_35_TURBO:
        llm = get_openai_llm()
    elif llm_type == LLMType.GPT_4:
        llm = get_openai_llm(gpt_4=True)
    elif llm_type == LLMType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
    else:
        raise ValueError("Unexpected llm type")
    return get_chatbot_executor(llm, system_message, checkpointer)


class ConfigurableChatBot(RunnableBinding):
    llm: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    def __init__(
        self,
        *,
        llm: LLMType = LLMType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        chatbot = get_chatbot(
                llm,
                system_message,
                checkpointer if checkpointer else get_pg_checkpoint_saver()
            )

        super().__init__(
            llm=llm,
            system_message=system_message,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        )

class ConfigurableRetrieval(RunnableBinding):
    llm_type: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    assistant_id: Optional[str] = None

    def __init__(
        self,
        *,
        llm_type: LLMType = LLMType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        retriever = get_retriever(assistant_id)
        if llm_type == LLMType.GPT_35_TURBO:
            llm = get_openai_llm()
        elif llm_type == LLMType.GPT_4:
            llm = get_openai_llm(gpt_4=True)
        elif llm_type == LLMType.AZURE_OPENAI:
            llm = get_openai_llm(azure=True)
        else:
            raise ValueError("Unexpected llm type")
        chatbot = get_retrieval_executor(
                llm,
                system_message,
                retriever,
                checkpointer if checkpointer else get_pg_checkpoint_saver()
            )
        super().__init__(
            llm_type=llm_type,
            system_message=system_message,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        )

chatbot = (
    ConfigurableChatBot(llm=LLMType.GPT_35_TURBO)
    .configurable_fields(
        llm=ConfigurableField(id="llm_type", name="LLM Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
    )
    .with_types(input_type=Sequence[AnyMessage], output_type=Sequence[AnyMessage])
)

chat_retrieval = (
    ConfigurableRetrieval(llm_type=LLMType.GPT_35_TURBO)
    .configurable_fields(
        llm_type=ConfigurableField(id="llm_type", name="LLM Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
    )
    .with_types(input_type=Sequence[AnyMessage], output_type=Sequence[AnyMessage])
)


agent = (
    ConfigurableAgent(
        agent=AgentType.GPT_35_TURBO,
        tools=[],
        system_message=DEFAULT_SYSTEM_MESSAGE,
        retrieval_description=RETRIEVAL_DESCRIPTION,
        assistant_id=None,
    )
    .configurable_fields(
        agent=ConfigurableField(id="agent_type", name="Agent Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        interrupt_before_action=ConfigurableField(
            id="interrupt_before_action",
            name="Tool Confirmation",
            description="If Yes, you'll be prompted to continue before each tool is executed.\nIf No, tools will be executed automatically by the agent.",
        ),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
        tools=ConfigurableFieldMultiOption(
            id="tools",
            name="Tools",
            options=TOOL_OPTIONS,
            default=[],
        ),
        retrieval_description=ConfigurableField(
            id="retrieval_description", name="Retrieval Description"
        ),
    )
    .configurable_alternatives(
        ConfigurableField(id="type", name="Bot Type"),
        default_key="agent",
        prefix_keys=True,
        chatbot=chatbot,
        chat_retrieval=chat_retrieval,
    )
    .with_types(input_type=Sequence[AnyMessage], output_type=Sequence[AnyMessage])
)

if __name__ == "__main__":
    import asyncio

    from langchain.schema.messages import HumanMessage

    async def run():
        async for m in agent.astream_events(
            HumanMessage(content="whats your name"),
            config={"configurable": {"thread_id": "test1"}},
            version="v1",
        ):
            print(m)

    asyncio.run(run())
