from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Union, Iterator, AsyncIterator, AsyncGenerator
from functools import cached_property

from langchain_core.messages import AnyMessage
from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
    RunnableSerializable,
    RunnableConfig,
)
from langchain_core.runnables.utils import Input, Output
from langgraph.graph.message import Messages
from langgraph.pregel import Pregel

from stack.app.agents.tools_agent import get_tools_agent_executor
from stack.app.agents.xml_agent import get_xml_agent_executor
from stack.app.agents.chatbot import get_chatbot_executor
from stack.app.core.configuration import get_settings
from stack.app.schema.assistant import AgentType, LLMType
from stack.app.core.llms import (
    get_anthropic_llm,
    get_google_llm,
    get_mixtral_fireworks,
    get_ollama_llm,
    get_openai_llm,
)
from stack.app.agents.retrieval import get_retrieval_executor
from stack.app.agents.tools import (
    RETRIEVAL_DESCRIPTION,
    TOOLS,
    ActionServer,
    Arxiv,
    AvailableTools,
    Connery,
    DallE,
    DDGSearch,
    PubMed,
    Retrieval,
    Tavily,
    TavilyAnswer,
    Wikipedia,
    YouSearch,
    SecFilings,
    PressReleases,
    get_retrieval_tool,
    get_retriever,
)

Tool = Union[
    ActionServer,
    Connery,
    DDGSearch,
    Arxiv,
    YouSearch,
    PubMed,
    Wikipedia,
    Tavily,
    TavilyAnswer,
    Retrieval,
    DallE,
    SecFilings,
    PressReleases,
]

DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


def get_llm(llm_type: LLMType):
    if llm_type == LLMType.GPT_4O_MINI:
        llm = get_openai_llm()
    elif llm_type == LLMType.GPT_4 or llm_type == LLMType.GPT_4_TURBO:
        llm = get_openai_llm(model="gpt-4-turbo")
    elif llm_type == LLMType.GPT_4O:
        llm = get_openai_llm(model="gpt-4o")
    elif llm_type == LLMType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
    elif llm_type == LLMType.ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm()
    elif llm_type == LLMType.BEDROCK_ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm(bedrock=True)
    elif llm_type == LLMType.GEMINI:
        llm = get_google_llm()
    elif llm_type == LLMType.MIXTRAL:
        llm = get_mixtral_fireworks()
    elif llm_type == LLMType.OLLAMA:
        llm = get_ollama_llm()
    else:
        raise ValueError(f"Unexpected llm type: {llm_type}")
    return llm


def get_agent_executor(
    tools: list,
    agent: AgentType,
    system_message: str,
    interrupt_before_action: bool,
):
    if agent == AgentType.GPT_4O_MINI:
        llm = get_openai_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.GPT_4:
        llm = get_openai_llm(model="gpt-4-turbo")
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.GPT_4O:
        llm = get_openai_llm(model="gpt-4o")
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.BEDROCK_ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm(bedrock=True)
        return get_xml_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.GEMINI:
        llm = get_google_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )
    elif agent == AgentType.OLLAMA:
        llm = get_ollama_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action
        )

    else:
        raise ValueError("Unexpected agent type")



class ConfigurableAgent(RunnableBinding[Messages, Sequence[AnyMessage]]):
    """A configurable agent that can be used in a RunnableSequence."""
    
    tools: Sequence[Tool]
    agent: AgentType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    retrieval_description: str = RETRIEVAL_DESCRIPTION
    interrupt_before_action: bool = False
    assistant_id: Optional[str] = None
    # thread_id: Optional[str] = None
    thread_id: str = ""
    user_id: Optional[str] = None

    def _create_tool(
        self,
        tool: Union[dict, Tool],
        assistant_id: Optional[str],
        # thread_id: Optional[str],
        thread_id: str,
        retrieval_description: str,
    ) -> Union[Tool, list[Tool]]:
        """Helper method to create tool instances."""
        if isinstance(tool, dict):
            tool_type = AvailableTools(tool["type"])
        else:
            tool_type = tool.type

        if tool_type == AvailableTools.RETRIEVAL:
            if assistant_id is None or thread_id == "":
                raise ValueError(
                    "Both assistant_id and thread_id must be provided if Retrieval tool is used"
                )
            config = tool.config if isinstance(tool, Tool) else tool.get("config", {})
            return get_retrieval_tool(
                assistant_id, thread_id, retrieval_description, config
            )
        else:
            tool_obj = (
                tool if isinstance(tool, Tool) else self._convert_dict_to_tool(tool)
            )
            tool_config = tool_obj.config or {}
            return TOOLS[tool_obj.type](**tool_config)


    def __init__(
        self,
        *,
        tools: Sequence[Tool],
        agent: AgentType = AgentType.GPT_4O_MINI,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        thread_id: str = "",
        retrieval_description: str = RETRIEVAL_DESCRIPTION,
        interrupt_before_action: bool = False,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        settings = get_settings()
        others.pop("bound", None)

        _tools = []
        for tool in tools:
            created_tool = self._create_tool(
                tool, assistant_id, thread_id, retrieval_description
            )
            if isinstance(created_tool, list):
                _tools.extend(created_tool)
            else:
                _tools.append(created_tool)

        _agent = get_agent_executor(
            _tools, agent, system_message, interrupt_before_action
        )
        agent_executor = _agent.with_config(
            {"recursion_limit": settings.LANGGRAPH_RECURSION_LIMIT}
        )
        super().__init__(
            tools=tools,
            agent=agent,
            system_message=system_message,
            retrieval_description=retrieval_description,
            bound=agent_executor,
            kwargs=kwargs or {},
            config=config or {},
        )


def get_configured_agent() -> Pregel:
    """Get a configured agent instance."""
    initial_agent = ConfigurableAgent(
        tools=[],
        agent=AgentType.GPT_4O_MINI,
        system_message=DEFAULT_SYSTEM_MESSAGE,
        retrieval_description=RETRIEVAL_DESCRIPTION,
        assistant_id=None,
        # thread_id=None,
        thread_id="",
        interrupt_before_action=False,
    )
    
    return (initial_agent
        .configurable_fields(
            agent=ConfigurableField(id="agent_type", name="Agent Type"),
            system_message=ConfigurableField(id="system_message", name="Instructions"),
            interrupt_before_action=ConfigurableField(
                id="interrupt_before_action",
                name="Tool Confirmation",
                description="If Yes, you'll be prompted to continue before each tool is executed.\nIf No, tools will be executed automatically by the agent.",
            ),
            assistant_id=ConfigurableField(
                id="assistant_id",
                name="Assistant ID",
                is_shared=True,
                annotation=Optional[str],
            ),
            thread_id=ConfigurableField(
                id="thread_id",
                name="Thread ID",
                is_shared=True,
                annotation=str,
            ),
            tools=ConfigurableField(id="tools", name="Tools"),
            retrieval_description=ConfigurableField(
                id="retrieval_description",
                name="Retrieval Description"
            ),
        )
        .configurable_alternatives(
            ConfigurableField(id="type", name="Bot Type"),
            default_key="agent",
            prefix_keys=True,
        )
        .with_types(
            input_type=Messages,
            output_type=Sequence[AnyMessage],
        ))

if __name__ == "__main__":
    import asyncio

    from langchain.schema.messages import HumanMessage

    async def run():
        agent = get_configured_agent()
        async for m in agent.astream_events(
            HumanMessage(content="whats your name"),
            config={"configurable": {"user_id": "2", "thread_id": "test1"}},
            version="v1",
        ):
            print(m)

    asyncio.run(run())
