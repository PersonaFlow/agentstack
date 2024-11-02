from typing import Any, Dict, Mapping, Optional

from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
    Runnable,
)

from stack.app.schema.assistant import LLMType
from stack.app.agents.llm import get_llm

from stack.app.agents.retrieval import get_retrieval_executor
from stack.app.agents.tools import get_retriever


DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


class ConfigurableRetrieval(RunnableBinding):
    llm_type: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    assistant_id: Optional[str] = None
    thread_id: str = ""
    user_id: Optional[str] = None

    def __init__(
        self,
        *,
        llm_type: LLMType = LLMType.GPT_4O_MINI,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        thread_id: str = "",
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        retriever = get_retriever(assistant_id, thread_id)
        llm = get_llm(llm_type)
        chatbot = get_retrieval_executor(llm, retriever, system_message)
        super().__init__(
            llm_type=llm_type,
            system_message=system_message,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        ) # type: ignore

def get_configured_chat_retrieval() -> Runnable:
    initial = ConfigurableRetrieval(
        llm_type=LLMType.GPT_4O_MINI,
        system_message=DEFAULT_SYSTEM_MESSAGE
    )
    return (
        initial.configurable_fields(
            llm_type=ConfigurableField(
                id="llm_type", 
                name="LLM Type"
            ),
            system_message=ConfigurableField(
                id="system_message", 
                name="Instructions"
            ),
            assistant_id=ConfigurableField(
                id="assistant_id", 
                name="Assistant ID",
                is_shared=True
            ),
            thread_id=ConfigurableField(
                id="thread_id", 
                name="Thread ID", 
                is_shared=True
            ),
        )
        .with_types(
            input_type=Dict[str, Any],
            output_type=Dict[str, Any],
        )
    )


