from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Generic
from langchain_core.messages import BaseMessage, AIMessage

# Define generic types for input and state
InputType = TypeVar('InputType')
StateType = TypeVar('StateType')

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

class ToolsAgentStateHandler(BaseStateHandler[List[BaseMessage], Dict[str, Any]]):
    """Handler for the tools agent architecture."""
    
    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        # Tools agent already expects messages list
        return input_data
        
    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        if not isinstance(state, dict):
            return []
        messages = state.get("messages", [])
        return messages if isinstance(messages, list) else [messages]


class ChatRetrievalStateHandler(BaseStateHandler[List[BaseMessage], Dict[str, Any]]):
    """Handler for the chat retrieval architecture."""
    
    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, list):
            return {
                "messages": input_data,
                "msg_count": len(input_data)
            }
        return input_data
        
    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        if not isinstance(state, dict):
            return []
        messages = state.get("messages", [])
        if isinstance(messages, BaseMessage):
            return [messages]
        return messages if isinstance(messages, list) else [messages]
    

class CRAGStateHandler(BaseStateHandler[Dict[str, Any], Dict[str, Any]]):
    """Handler for the CRAG architecture."""
    
    def format_initial_state(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, list):
            # Format initial state for CRAG
            question = input_data[0].content if input_data else ""
            return {
                "messages": input_data,
                "question": question,
                "generation": "",
                "web_search_needed": False,
                "documents": [],
                "iteration_count": 0
            }
        return input_data
        
    def extract_messages(self, state: Dict[str, Any]) -> List[BaseMessage]:
        if not isinstance(state, dict):
            return []
        generation = state.get("generation")
        if generation:
            return [AIMessage(content=generation)]
        return []


# Registry that maps architecture types to their handlers
class StateRegistry:
    """Registry for agent architectures."""
    
    def __init__(self):
        self._architectures: Dict[str, BaseStateHandler] = {
            "agent": ToolsAgentStateHandler(),
            "chat_retrieval": ChatRetrievalStateHandler(),
            "corrective_rag": CRAGStateHandler()
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

# Create a global registry instance
state_registry = StateRegistry()