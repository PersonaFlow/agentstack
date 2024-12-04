from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Generic, Optional, Union
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

# Define generic types for input and state
InputType = TypeVar("InputType")
StateType = TypeVar("StateType")


class BaseStateHandler(Generic[InputType, StateType], ABC):
    """Base class for different agent architectures."""

    @abstractmethod
    def format_initial_state(self, input_data: Any) -> StateType:
        """Format raw input into the initial state for this architecture."""
        pass

    @abstractmethod
    def extract_messages(self, state: StateType) -> List[BaseMessage]:
        """Extract messages from the architecture's state format."""
        pass

    @abstractmethod
    def prepare_config(
        self,
        input_data: Any,
        config: RunnableConfig,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> tuple[StateType, RunnableConfig]:
        """Prepare the input state and config for this architecture."""
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data format for this architecture."""
        pass


class ToolsAgentStateHandler(BaseStateHandler[List[BaseMessage], Dict[str, Any]]):
    """Handler for the tools agent architecture."""

    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        # Tools agent expects messages list
        return input_data

    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        if not isinstance(state, dict):
            return []
        messages = state.get("messages", [])
        return messages if isinstance(messages, list) else [messages]

    def prepare_config(
        self,
        input_data: Any,
        config: RunnableConfig,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], RunnableConfig]:
        # Tools agent doesn't need special config handling
        return input_data, config

    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, list)


class ChatRetrievalStateHandler(BaseStateHandler[List[BaseMessage], Dict[str, Any]]):
    """Handler for the chat retrieval architecture."""

    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, list):
            return {"messages": input_data, "msg_count": len(input_data)}
        return input_data

    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        if not isinstance(state, dict):
            return []
        messages = state.get("messages", [])
        if isinstance(messages, BaseMessage):
            return [messages]
        return messages if isinstance(messages, list) else [messages]

    def prepare_config(
        self,
        input_data: Any,
        config: RunnableConfig,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], RunnableConfig]:
        formatted_state = self.format_initial_state(input_data)
        return formatted_state, config

    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, list)


class CRAGStateHandler(BaseStateHandler[Dict[str, Any], Dict[str, Any]]):
    """Handler for the CRAG architecture."""

    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, list):
            # question = input_data[0].content if input_data else ""
            question = input_data[0].get("content") if input_data else ""
            return {
                "messages": input_data,
                "question": question,
                "generation": "",
                "web_search_needed": False,
                "documents": [],
                "iteration_count": 0,
                "actions": [],
            }
        return input_data

    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        """Extract messages including both actions and generation."""
        if not isinstance(state, dict):
            return []

        messages = []

        # Add any action messages
        actions = state.get("actions", [])
        messages.extend(actions)

        # Add generation if present
        generation = state.get("generation")
        if generation:
            messages.append(AIMessage(content=generation))

        return messages

    def prepare_config(
        self,
        input_data: Any,
        config: RunnableConfig,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], RunnableConfig]:
        formatted_state = self.format_initial_state(input_data)

        if "configurable" not in config:
            config["configurable"] = {}

        config["configurable"].update(
            {
                "assistant_id": assistant_id,
                "thread_id": thread_id,
            }
        )

        return formatted_state, config

    def validate_input(self, input_data: Any) -> bool:
        if not isinstance(input_data, list) or not input_data:
            return False
        return all(isinstance(msg, dict) and "content" in msg for msg in input_data)


class StateRegistry:
    """Registry for agent architectures."""

    def __init__(self):
        self._architectures: Dict[str, BaseStateHandler] = {
            "agent": ToolsAgentStateHandler(),
            "chat_retrieval": ChatRetrievalStateHandler(),
            "corrective_rag": CRAGStateHandler(),
        }

    def get_architecture(self, type_name: str) -> BaseStateHandler:
        """Get the appropriate architecture handler."""
        architecture = self._architectures.get(type_name)
        if not architecture:
            raise ValueError(f"Unsupported architecture type: {type_name}")
        return architecture

    def register_state_handler(self, type_name: str, architecture: BaseStateHandler):
        """Register a new architecture type."""
        self._architectures[type_name] = architecture

    def prepare_state_and_config(
        self,
        architecture_type: str,
        input_data: Any,
        config: RunnableConfig,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> tuple[Any, RunnableConfig]:
        """Prepare the state and config for a given architecture type."""
        handler = self.get_architecture(architecture_type)

        if not handler.validate_input(input_data):
            raise ValueError(
                f"Invalid input format for architecture type: {architecture_type}"
            )

        return handler.prepare_config(input_data, config, assistant_id, thread_id)


# Create a global registry instance
state_registry = StateRegistry()
