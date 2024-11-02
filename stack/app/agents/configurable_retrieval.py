from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from langchain_core.messages import AnyMessage
from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
    RunnableSerializable,
)
from langgraph.graph.message import Messages
from langgraph.pregel import Pregel

from stack.app.agents.tools_agent import get_tools_agent_executor

# from stack.app.agents.xml_agent import get_xml_agent_executor
# from stack.app.agents.chatbot import get_chatbot_executor
from stack.app.core.configuration import get_settings
from stack.app.schema.assistant import AgentType, LLMType
from stack.app.core.llms import (
    get_anthropic_llm,
    get_google_llm,
    get_mixtral_fireworks,
    get_ollama_llm,
    get_openai_llm,
)

# from stack.app.agents.retrieval import get_retrieval_executor
# from stack.app.core.datastore import get_checkpointer
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


# def get_chatbot(
#     llm_type: LLMType,
#     system_message: str,
# ):
#     llm = get_llm(llm_type)
#     return get_chatbot_executor(llm, system_message)


# class ConfigurableChatBot(RunnableBinding):
#     llm: LLMType
#     system_message: str = DEFAULT_SYSTEM_MESSAGE
#     user_id: Optional[str] = None

#     def __init__(
#         self,
#         *,
#         llm: LLMType = LLMType.GPT_4O_MINI,
#         system_message: str = DEFAULT_SYSTEM_MESSAGE,
#         kwargs: Optional[Mapping[str, Any]] = None,
#         config: Optional[Mapping[str, Any]] = None,
#         **others: Any,
#     ) -> None:
#         others.pop("bound", None)

#         chatbot = get_chatbot(llm, system_message)
#         super().__init__(
#             llm=llm,
#             system_message=system_message,
#             bound=chatbot,
#             kwargs=kwargs or {},
#             config=config or {},
#         )


# chatbot = (
#     ConfigurableChatBot(llm=LLMType.GPT_4O_MINI)
#     .configurable_fields(
#         llm=ConfigurableField(id="llm_type", name="LLM Type"),
#         system_message=ConfigurableField(id="system_message", name="Instructions"),
#     )
#     .with_types(
#         input_type=Messages,
#         output_type=Sequence[AnyMessage],
#     )
# )


# class ConfigurableRetrieval(RunnableBinding):
#     llm_type: LLMType
#     system_message: str = DEFAULT_SYSTEM_MESSAGE
#     assistant_id: Optional[str] = None
#     thread_id: Optional[str] = None
#     user_id: Optional[str] = None

#     def __init__(
#         self,
#         *,
#         llm_type: LLMType = LLMType.GPT_4O_MINI,
#         system_message: str = DEFAULT_SYSTEM_MESSAGE,
#         assistant_id: Optional[str] = None,
#         thread_id: Optional[str] = None,
#         kwargs: Optional[Mapping[str, Any]] = None,
#         config: Optional[Mapping[str, Any]] = None,
#         **others: Any,
#     ) -> None:
#         others.pop("bound", None)
#         retriever = get_retriever(assistant_id, thread_id)
#         llm = get_llm(llm_type)
#         chatbot = get_retrieval_executor(llm, retriever, system_message)
#         super().__init__(
#             llm_type=llm_type,
#             system_message=system_message,
#             bound=chatbot,
#             kwargs=kwargs or {},
#             config=config or {},
#         )


# chat_retrieval = (
#     ConfigurableRetrieval(llm_type=LLMType.GPT_4O_MINI)
#     .configurable_fields(
#         llm_type=ConfigurableField(id="llm_type", name="LLM Type"),
#         system_message=ConfigurableField(id="system_message", name="Instructions"),
#         assistant_id=ConfigurableField(
#             id="assistant_id", name="Assistant ID", is_shared=True
#         ),
#         thread_id=ConfigurableField(id="thread_id", name="Thread ID", is_shared=True),
#     )
#     .with_types(
#         input_type=Dict[str, Any],
#         output_type=Dict[str, Any],
#     )
# )
