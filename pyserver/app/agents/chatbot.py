from langchain_core.language_models.base import LanguageModelLike
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.graph.message import MessageGraph
from langgraph.checkpoint import BaseCheckpointSaver


def get_chatbot_executor(
    llm: LanguageModelLike,
    system_message: str,
    checkpointer: BaseCheckpointSaver,
):
    def _get_messages(messages):
        return [SystemMessage(content=system_message)] + messages

    chatbot = _get_messages | llm

    workflow = MessageGraph()
    workflow.add_node("chatbot", chatbot)
    workflow.set_entry_point("chatbot")
    workflow.add_edge("chatbot", END)
    app = workflow.compile(checkpointer=checkpointer)
    return app
