# from enum import Enum
# from typing import Any, Dict, Mapping, Optional, Sequence, Union

# from langchain_core.messages import AnyMessage
# from langchain_core.runnables import (
#     ConfigurableField,
#     RunnableBinding,
#     RunnableSerializable,
# )
# from langgraph.graph.message import Messages

# from stack.app.agents.xml_agent import get_xml_agent_executor
# from stack.app.agents.chatbot import get_chatbot_executor
# from stack.app.core.configuration import get_settings
# from stack.app.schema.assistant import AgentType, LLMType

# from stack.app.agents.retrieval import get_retrieval_executor
# from stack.app.core.datastore import get_checkpointer
# from stack.app.agents.tools import (
#     RETRIEVAL_DESCRIPTION,
#     TOOLS,
#     ActionServer,
#     Arxiv,
#     AvailableTools,
#     Connery,
#     DallE,
#     DDGSearch,
#     PubMed,
#     Retrieval,
#     Tavily,
#     TavilyAnswer,
#     Wikipedia,
#     YouSearch,
#     SecFilings,
#     PressReleases,
#     get_retrieval_tool,
#     get_retriever,
# )

# Tool = Union[
#     ActionServer,
#     Connery,
#     DDGSearch,
#     Arxiv,
#     YouSearch,
#     PubMed,
#     Wikipedia,
#     Tavily,
#     TavilyAnswer,
#     Retrieval,
#     DallE,
#     SecFilings,
#     PressReleases,
# ]

# DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


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
