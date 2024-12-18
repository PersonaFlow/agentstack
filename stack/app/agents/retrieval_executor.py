from typing import List, TypedDict, Dict, Any, Union, cast
from uuid import uuid4
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, HumanMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph, START
from stack.app.core.datastore import get_checkpointer


class AgentState(TypedDict):
    messages: List[Union[BaseMessage, Dict]]
    msg_count: int


def get_retrieval_executor(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    system_message: str,
):
    def _convert_to_message(msg: Union[BaseMessage, Dict]) -> BaseMessage:
        """Convert dictionary to appropriate message type if needed."""
        if isinstance(msg, BaseMessage):
            return msg

        msg_type = msg.get("type", "").lower()
        if msg_type == "human":
            return HumanMessage(
                content=msg.get("content", ""),
                additional_kwargs=msg.get("additional_kwargs", {}),
            )
        elif msg_type == "ai":
            return AIMessage(
                content=msg.get("content", ""),
                additional_kwargs=msg.get("additional_kwargs", {}),
                tool_calls=msg.get("tool_calls", []),
            )
        elif msg_type == "system":
            return SystemMessage(content=msg.get("content", ""))
        else:
            # Default to human message if type unknown
            return HumanMessage(content=str(msg.get("content", "")))

    def _get_messages(messages: List[Union[BaseMessage, Dict]]) -> List[BaseMessage]:
        # Convert all messages and filter appropriately
        chat_history = []
        last_tool_result = None

        for m in messages:
            msg = _convert_to_message(m)
            if isinstance(msg, AIMessage):
                if not getattr(msg, "tool_calls", None):
                    chat_history.append(msg)
            if isinstance(msg, HumanMessage):
                chat_history.append(msg)
            # Capture last tool result for context
            if getattr(msg, "additional_kwargs", {}).get("tool_output"):
                last_tool_result = msg

        # If we have retrieval results, format them as context
        context = ""
        if last_tool_result and last_tool_result.additional_kwargs.get("tool_output"):
            tool_output = last_tool_result.additional_kwargs["tool_output"]
            if isinstance(tool_output, list):
                context = "\n\n".join(doc.page_content for doc in tool_output)

        # Return formatted messages
        return [
            SystemMessage(content=f"{system_message}\n\nContext:\n{context}"),
            *chat_history,
        ]

    async def invoke_retrieval(state: AgentState) -> Dict[str, Any]:
        messages = [_convert_to_message(m) for m in state["messages"]]

        # For first message, use direct query
        if len(messages) == 1:
            # Extract query from first message
            msg_content = messages[-1].content
            query = msg_content.replace(
                "Use the retrieval tool to answer the question:", ""
            ).strip()
        else:
            # For follow-ups, use search prompt
            search_prompt = ChatPromptTemplate.from_template(
                """Given the conversation below, generate a search query to find relevant information.
                Return ONLY the search query, nothing else.
                
                Conversation:
                {conversation}
                """
            )

            # Format conversation history
            conversation = "\n".join(
                f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
                for m in messages
                if not getattr(m, "tool_calls", None)
            )

            query = await search_prompt.ainvoke(
                {"conversation": conversation},
                config={"configurable": {"tags": ["nostream"]}},
            )
            query = query.content.strip()

        # Create tool call message
        tool_call_id = uuid4().hex
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": tool_call_id,
                            "name": "retrieval",
                            "args": {"query": query},
                        }
                    ],
                )
            ]
        }

    async def retrieve(state: AgentState) -> Dict[str, Any]:
        messages = [_convert_to_message(m) for m in state["messages"]]
        if not messages:
            return {"messages": [], "msg_count": 0}

        # Get query from tool call
        last_message = messages[-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": [], "msg_count": 0}

        tool_call = last_message.tool_calls[0]
        query = tool_call["args"]["query"]

        # Get documents
        docs = await retriever.aget_relevant_documents(query)

        # Return tool result message
        return {
            "messages": [
                AIMessage(
                    content="",
                    additional_kwargs={
                        "tool_call_id": tool_call["id"],
                        "tool_name": "retrieval",
                        "tool_output": docs,
                    },
                )
            ],
            "msg_count": 1,
        }

    async def generate_response(state: AgentState) -> Dict[str, Any]:
        # Convert and format messages
        messages = _get_messages(state["messages"])

        # Generate response
        response = await llm.ainvoke(messages)

        return {"messages": [response], "msg_count": 1}

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("invoke_retrieval", invoke_retrieval)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate_response)

    # Add edges
    workflow.set_entry_point("invoke_retrieval")
    workflow.add_edge("invoke_retrieval", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    # Compile with checkpointer
    checkpoint = get_checkpointer()
    app = workflow.compile(checkpointer=checkpoint)
    return app
