from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, BaseMessage
from uuid import uuid4


class CRAGActionMetadata(BaseModel):
    """Metadata for CRAG actions."""

    action_type: str = Field(..., description="Type of action being performed")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional details about the action"
    )

    class Config:
        arbitrary_types_allowed = True


class CRAGAction(BaseModel):
    """Structure for CRAG action messages."""

    id: str = Field(default_factory=lambda: f"crag_{uuid4().hex}")
    type: str = Field(default="function")
    name: str = Field(..., description="Name of the CRAG action")
    arguments: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class CRAGMessage(AIMessage):
    """Message type for CRAG events."""

    crag_actions: Optional[List[CRAGAction]] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_gradation_step(
        cls, documents: List[Any], scores: List[float]
    ) -> "CRAGMessage":
        """Create a message for document grading step."""
        return cls(
            content="",
            additional_kwargs={
                "crag_actions": [
                    {
                        "id": f"crag_{uuid4().hex}",
                        "type": "function",
                        "name": "grade_documents",
                        "arguments": {
                            "results": [
                                {"content": doc.page_content, "score": score}
                                for doc, score in zip(documents, scores)
                            ]
                        },
                    }
                ]
            },
        )

    @classmethod
    def from_retrieval_step(cls, query: str) -> "CRAGMessage":
        """Create a message for retrieval step."""
        return cls(
            content="",
            additional_kwargs={
                "crag_actions": [
                    {
                        "id": f"crag_{uuid4().hex}",
                        "type": "function",
                        "name": "retrieve",
                        "arguments": {"query": query},
                    }
                ]
            },
        )

    @classmethod
    def from_query_transformation(
        cls, original: str, transformed: str
    ) -> "CRAGMessage":
        """Create a message for query transformation step."""
        return cls(
            content="",
            additional_kwargs={
                "crag_actions": [
                    {
                        "id": f"crag_{uuid4().hex}",
                        "type": "function",
                        "name": "transform_query",
                        "arguments": {
                            "original_query": original,
                            "transformed_query": transformed,
                        },
                    }
                ]
            },
        )

    @classmethod
    def from_web_search(cls, query: str) -> "CRAGMessage":
        """Create a message for web search step."""
        return cls(
            content="",
            additional_kwargs={
                "crag_actions": [
                    {
                        "id": f"crag_{uuid4().hex}",
                        "type": "function",
                        "name": "web_search",
                        "arguments": {"query": query},
                    }
                ]
            },
        )


def format_crag_state_as_message(
    state: Dict[str, Any], action: str, details: Optional[Dict[str, Any]] = None
) -> CRAGMessage:
    """Format a CRAG state update as a structured message.

    Args:
        state: Current state of the CRAG workflow
        action: Name of the action being performed
        details: Optional additional details about the action

    Returns:
        CRAGMessage with appropriate action information
    """
    if action == "retrieve":
        return CRAGMessage.from_retrieval_step(state["question"])
    elif action == "grade_documents":
        # Assume scores are added to details
        if not details or "scores" not in details:
            return CRAGMessage(content="")
        return CRAGMessage.from_gradation_step(state["documents"], details["scores"])
    elif action == "transform_query":
        return CRAGMessage.from_query_transformation(
            state.get("original_question", ""), state["question"]
        )
    elif action == "web_search" and state.get("web_search_needed"):
        return CRAGMessage.from_web_search(state["question"])

    # Default case - return empty message
    return CRAGMessage(content="")
