from typing import Optional, Sequence, Any, Mapping
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableBinding, ConfigurableField
from langgraph.graph.message import Messages

from .corrective_action_executor import get_crag_executor
from .llm import AgentType, get_llm
from .tools import AvailableTools, TOOLS, get_retriever, RetrievalConfigModel


class ConfigurableCorrectiveRAGAgent(RunnableBinding):
    """A configurable Corrective RAG agent that can be used in a
    RunnableSequence."""

    agent: AgentType = AgentType.GPT_4O_MINI
    system_prompt: str = (
        "You are a helpful AI assistant that evaluates document relevance."
    )
    question_rewriter_prompt: Optional[
        str
    ] = "You are an expert at reformulating questions to be clearer and more effective for search."
    max_corrective_iterations: int = 1
    enable_web_search: bool = True
    relevance_threshold: float = 0.7
    assistant_id: Optional[str] = None
    thread_id: str = ""
    retrieval_config: Optional[dict] = None

    def __init__(
        self,
        *,
        agent: AgentType = AgentType.GPT_4O_MINI,
        system_prompt: str = "You are a helpful AI assistant that evaluates document relevance.",
        question_rewriter_prompt: Optional[str] = None,
        max_corrective_iterations: int = 3,
        enable_web_search: bool = True,
        relevance_threshold: float = 0.7,
        assistant_id: Optional[str] = None,
        thread_id: str = "",
        # retrieval_config: Optional[dict] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        llm = get_llm(agent)
        web_search_tool = None
        if enable_web_search:
            web_search_getter = TOOLS[AvailableTools.TAVILY]
            web_search_tool = web_search_getter()

        retrieval_config = RetrievalConfigModel().to_dict()

        retriever = get_retriever(
            assistant_id=assistant_id, thread_id=thread_id, config=retrieval_config
        )

        crag = get_crag_executor(
            llm=llm,
            retriever=retriever,
            system_prompt=system_prompt,
            web_search_tool=web_search_tool if enable_web_search else None,
            question_rewriter_prompt=question_rewriter_prompt,
            max_corrective_iterations=max_corrective_iterations,
            enable_web_search=enable_web_search,
            relevance_threshold=relevance_threshold,
        )

        super().__init__(  # type: ignore[call-arg]
            agent=agent,
            system_prompt=system_prompt,
            question_rewriter_prompt=question_rewriter_prompt,
            max_corrective_iterations=max_corrective_iterations,
            enable_web_search=enable_web_search,
            relevance_threshold=relevance_threshold,
            assistant_id=assistant_id,
            thread_id=thread_id,
            retrieval_config=retrieval_config,
            bound=crag,
            kwargs=kwargs or {},
            config=config or {},
        )


def get_configured_crag() -> ConfigurableCorrectiveRAGAgent:
    """Get a configured CRAG instance."""

    initial_agent = ConfigurableCorrectiveRAGAgent(
        agent=AgentType.GPT_4O_MINI,
        system_prompt="You are a helpful AI assistant that evaluates document relevance.",
        question_rewriter_prompt="You are a question re-writer that converts an input question to a better version that is optimized for web search. Look at the input and try to reason about the underlying semantic intent / meaning.",
        max_corrective_iterations=3,
        enable_web_search=True,
        relevance_threshold=0.7,
        assistant_id=None,
        thread_id="",
    )

    return initial_agent.configurable_fields(
        agent=ConfigurableField(
            id="agent_type", name="Agent Type", description="The type of agent to use"
        ),
        system_prompt=ConfigurableField(
            id="system_prompt",
            name="System Prompt",
            description="The system prompt for the corrective RAG agent",
        ),
        question_rewriter_prompt=ConfigurableField(
            id="question_rewriter_prompt",
            name="Question Rewriter Prompt",
            description="The prompt for rewriting questions to be more effective",
        ),
        max_corrective_iterations=ConfigurableField(
            id="max_corrective_iterations",
            name="Max Corrective Iterations",
            description="Maximum number of correction iterations",
        ),
        enable_web_search=ConfigurableField(
            id="enable_web_search",
            name="Enable Web Search",
            description="Whether to enable web search for supplemental retrieval",
        ),
        relevance_threshold=ConfigurableField(
            id="relevance_threshold",
            name="Relevance Threshold",
            description="Threshold for document relevance scoring",
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
    ).with_types(
        input_type=Messages,
        output_type=Sequence[BaseMessage],
    )  # type: ignore[return-value]
