from typing import Any, Dict, Mapping, Optional, Union

from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
    Runnable,
)

from stack.app.agents.llm import get_llm, LLMType

from stack.app.agents.retrieval_executor import get_retrieval_executor
from .tools import get_retriever, RetrievalConfigModel


DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


class ConfigurableRetrieval(RunnableBinding):
    llm_type: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    assistant_id: Optional[str] = None
    thread_id: str = ""
    user_id: Optional[str] = None
    # retrieval_config: Optional[Union[RetrievalConfigModel, dict]]

    def __init__(
        self,
        *,
        llm_type: LLMType = LLMType.GPT_4O_MINI,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        thread_id: str = "",
        # retrieval_config: Optional[Union[RetrievalConfigModel, dict]],
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)

        # # If retrieval_config is provided in config, use that
        # if config and "retrieval_config" in config.get("configurable", {}):
        #     retrieval_config = RetrievalConfigModel(**config["configurable"]["retrieval_config"])
        # # Otherwise use the passed retrieval_config or create a new one with defaults
        # final_config = retrieval_config or RetrievalConfigModel()

        # config_dict = (
        #     final_config.model_dump()
        #     if hasattr(final_config, 'model_dump')
        #     else final_config.dict()
        # )

        retrieval_config = RetrievalConfigModel().to_dict()

        retriever = get_retriever(
            assistant_id=assistant_id, thread_id=thread_id, config=retrieval_config
        )

        llm = get_llm(llm_type)
        chatbot = get_retrieval_executor(llm, retriever, system_message)
        super().__init__(
            llm_type=llm_type,
            system_message=system_message,
            # retrieval_config=config_dict,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        )  # type: ignore


def get_configured_chat_retrieval() -> Runnable:
    initial = ConfigurableRetrieval(
        llm_type=LLMType.GPT_4O_MINI, system_message=DEFAULT_SYSTEM_MESSAGE
    )
    return initial.configurable_fields(
        llm_type=ConfigurableField(id="llm_type", name="LLM Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
        thread_id=ConfigurableField(id="thread_id", name="Thread ID", is_shared=True),
        # retrieval_config=ConfigurableField(
        #     id="retrieval_config",
        #     name="Retrieval Configuration",
        #     description="Configuration for the retrieval system"
        # )
    ).with_types(
        input_type=Dict[str, Any],
        output_type=Dict[str, Any],
    )
