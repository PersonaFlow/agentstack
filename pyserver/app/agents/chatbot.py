from typing import Annotated, List
from langchain_core.language_models.base import LanguageModelLike
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import END
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph.state import StateGraph
from pyserver.app.schema.message_types import add_messages_liberal


def get_chatbot_executor(
    llm: LanguageModelLike,
    system_message: str,
    checkpointer: BaseCheckpointSaver,
):
    def _get_messages(messages):
        return [SystemMessage(content=system_message)] + messages

    chatbot = _get_messages | llm

    workflow = StateGraph(Annotated[List[BaseMessage], add_messages_liberal])
    workflow.add_node("chatbot", chatbot)
    workflow.set_entry_point("chatbot")
    workflow.add_edge("chatbot", END)
    app = workflow.compile(checkpointer=checkpointer)
    return app
