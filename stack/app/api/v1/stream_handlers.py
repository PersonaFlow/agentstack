from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Union
from langchain_core.messages import AIMessage, BaseMessage
import structlog

logger = structlog.get_logger(__name__)

class MessageHandler(ABC):
    """Abstract base class for handling different message/state formats."""
    
    @abstractmethod
    def extract_messages(self, chunk_data: Any) -> List[BaseMessage]:
        """Extract messages from a chunk of data.
        
        Args:
            chunk_data: Raw chunk data from the stream
            
        Returns:
            List of messages extracted from the chunk
        """
        pass

class ToolsAgentMessageHandler(MessageHandler):
    """Handles standard message format with a messages list."""
    
    def extract_messages(self, chunk_data: Any) -> List[BaseMessage]:
        """Extract messages from a chunk of data."""
        if not isinstance(chunk_data, dict):
            # If chunk_data is a list, flatten it
            if isinstance(chunk_data, list):
                # Handle both nested and unnested lists
                messages = []
                for item in chunk_data:
                    if isinstance(item, list):
                        messages.extend(item)
                    else:
                        messages.append(item)
                return messages
            return [chunk_data]
            
        messages = chunk_data.get("messages", [])
        if isinstance(messages, list):
            return messages
        return [messages]

class ChatRetrievalMessageHandler(MessageHandler):
    """Handles chat retrieval message format."""
    
    def extract_messages(self, chunk_data: Any) -> List[BaseMessage]:
        """Extract messages from the chat retrieval format."""
        if not isinstance(chunk_data, dict):
            return []
            
        messages = chunk_data.get("messages", [])
        return messages if isinstance(messages, list) else [messages]

class CRAGMessageHandler(MessageHandler):
    """Handles CRAG state format with generation field."""
    
    def extract_messages(self, chunk_data: Any) -> List[BaseMessage]:
        if not isinstance(chunk_data, dict):
            return []
            
        generation = chunk_data.get("generation")
        if generation:
            return [AIMessage(content=generation)]
            
        return []

# Add more handlers for different architectures here
# class NewArchitectureHandler(MessageHandler):
#     def extract_messages(self, chunk_data: Any) -> List[BaseMessage]:
#         # Handle the new architecture's format
#         pass

HandlerRegistry = Dict[str, MessageHandler]

class StreamProcessor:
    """Processes stream events and handles message extraction."""
    
    def __init__(self):
        self._handlers: HandlerRegistry = {
            "tools_agent": ToolsAgentMessageHandler(),
            "corrective_rag": CRAGMessageHandler(),
            "chat_retrieval": ChatRetrievalMessageHandler(),
            # Add more handlers here as new architectures are added
        }
        
    def _get_handler(self, config: Dict[str, Any]) -> MessageHandler:
        """Get the appropriate handler based on the configuration."""
        agent_type = config.get("configurable", {}).get("type", "standard")
        handler = self._handlers.get(agent_type)
        
        if not handler:
            logger.warning(
                f"No handler found for agent type {agent_type}, using standard handler"
            )
            handler = self._handlers["tools_agent"]
            
        return handler
        
    def process_chunk(
        self,
        event: Dict[str, Any],
        config: Dict[str, Any],
        messages: Dict[str, BaseMessage]
    ) -> List[BaseMessage]:
        """Process a chunk and extract new messages.
        
        Args:
            event: The stream event
            config: The agent configuration
            messages: Dictionary of existing messages
            
        Returns:
            List of new messages extracted from the chunk
        """
        chunk_data = event["data"]["chunk"]
        handler = self._get_handler(config)
        new_messages: List[BaseMessage] = []
        
        extracted_messages = handler.extract_messages(chunk_data)
        
        for msg in extracted_messages:
            msg_id = msg.id
            if msg_id not in messages or messages[msg_id] != msg:
                messages[msg_id] = msg
                new_messages.append(msg)
                
        return new_messages
    