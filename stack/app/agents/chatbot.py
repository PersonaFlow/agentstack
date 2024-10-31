from typing import Annotated, List
from langchain_core.language_models.base import LanguageModelLike
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import END
from langgraph.graph.state import StateGraph
from stack.app.schema.message_types import add_messages_liberal
from stack.app.core.datastore import get_checkpointer


def get_chatbot_executor(
    llm: LanguageModelLike,
    system_message: str,
):
    checkpointer = get_checkpointer()
    def _get_messages(messages):
        return [SystemMessage(content=system_message)] + messages

    chatbot = _get_messages | llm

    workflow = StateGraph(Annotated[List[BaseMessage], add_messages_liberal])
    workflow.add_node("chatbot", chatbot)
    workflow.set_entry_point("chatbot")
    workflow.add_edge("chatbot", END)
    app = workflow.compile(checkpointer=checkpointer)
    return app
