from typing import Any, Mapping, Optional, Sequence, Union, Type, Dict, cast
from langchain_core.messages import AnyMessage
from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
)
from langgraph.graph.message import Messages
from langgraph.pregel import Pregel

from stack.app.agents.tools_agent_executor import get_tools_agent_executor
from stack.app.agents.xml_agent import get_xml_agent_executor
from stack.app.agents.configurable_retrieval import get_configured_chat_retrieval
from stack.app.core.configuration import settings
from stack.app.schema.assistant import AgentType
from stack.app.agents.llm import (
    get_anthropic_llm,
    get_google_llm,
    get_ollama_llm,
    get_openai_llm,
)
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
    thread_id: str = ""
    user_id: Optional[str] = None

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

        super().__init__(  # type: ignore[call-arg]
            tools=tools,
            agent=agent,
            system_message=system_message,
            retrieval_description=retrieval_description,
            bound=agent_executor,
            kwargs=kwargs or {},
            config=config or {},
        )

    def _convert_dict_to_tool(self, tool_dict: dict) -> Tool:
        tool_type = AvailableTools(tool_dict["type"])

        # Map tool types to their corresponding classes
        tool_classes: Dict[
            AvailableTools,
            Type[
                Union[
                    ActionServer,
                    Connery,
                    DDGSearch,
                    Arxiv,
                    YouSearch,
                    PubMed,
                    Wikipedia,
                    Tavily,
                    TavilyAnswer,
                    DallE,
                    SecFilings,
                    PressReleases,
                ]
            ],
        ] = {
            AvailableTools.TAVILY: Tavily,
            AvailableTools.DDG_SEARCH: DDGSearch,
            AvailableTools.ARXIV: Arxiv,
            AvailableTools.YOU_SEARCH: YouSearch,
            AvailableTools.PUBMED: PubMed,
            AvailableTools.WIKIPEDIA: Wikipedia,
            AvailableTools.DALL_E: DallE,
            AvailableTools.SEC_FILINGS: SecFilings,
            AvailableTools.PRESS_RELEASES: PressReleases,
            AvailableTools.ACTION_SERVER: ActionServer,
            AvailableTools.CONNERY: Connery,
            AvailableTools.TAVILY_ANSWER: TavilyAnswer,
        }

        tool_class = tool_classes.get(tool_type)
        if not tool_class:
            raise ValueError(f"Unsupported tool type: {tool_type}")

        # Create tool instance using only the necessary override fields
        # All constant fields (type, description, multi_use) are handled by the class definition
        kwargs = {}
        if "config" in tool_dict:
            kwargs["config"] = tool_dict["config"]
        if "name" in tool_dict:
            kwargs["name"] = tool_dict["name"]

        return cast(Tool, tool_class(**kwargs))

    def _create_tool(
        self,
        tool: Union[dict, Tool],
        assistant_id: Optional[str],
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
            )  # type: ignore
        else:
            tool_obj = (
                tool if isinstance(tool, Tool) else self._convert_dict_to_tool(tool)
            )
            tool_config = tool_obj.config or {}
            return TOOLS[tool_obj.type](**tool_config)


def get_configured_agent() -> Pregel:
    """Get a configured agent instance."""
    initial_agent = ConfigurableAgent(
        tools=[],
        agent=AgentType.GPT_4O_MINI,
        system_message=DEFAULT_SYSTEM_MESSAGE,
        retrieval_description=RETRIEVAL_DESCRIPTION,
        assistant_id=None,
        thread_id="",
        interrupt_before_action=False,
    )

    return (
        initial_agent.configurable_fields(
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
                id="retrieval_description", name="Retrieval Description"
            ),
        )
        .configurable_alternatives(
            ConfigurableField(id="type", name="Bot Type"),
            default_key="agent",
            prefix_keys=True,
            # chat_retrieval=get_configured_chat_retrieval()
        )
        .with_types(
            input_type=Messages,
            output_type=Sequence[AnyMessage],
        )  # type: ignore[return-value]
    )


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
