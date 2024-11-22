import functools
import asyncio
from typing import Any, AsyncIterator, Dict, Optional, Sequence, Union
import structlog

import orjson
from langchain_core.messages import AnyMessage, BaseMessage, message_chunk_to_message
from langchain_core.runnables import Runnable, RunnableConfig
from stack.app.core.redis import RedisService
from .state_registry import state_registry

logger = structlog.get_logger(__name__)

MessagesStream = AsyncIterator[Union[list[AnyMessage], str]]

class StreamProcessor:
    """Processes stream events and handles message extraction."""
    
    def process_chunk(
        self,
        event: Dict[str, Any],
        config: Dict[str, Any],
        messages: Dict[str, BaseMessage]
    ) -> list[BaseMessage]:
        """Process a chunk and extract new messages."""
        chunk_data = event["data"]["chunk"]
        architecture_type = config.get("configurable", {}).get("type", "agent")
        
        # Get the appropriate architecture handler
        architecture = state_registry.get_architecture(architecture_type)
        
        # Format state if needed
        if isinstance(chunk_data, list) and event["event"] == "on_chain_start":
            chunk_data = architecture.format_initial_state(chunk_data)
            
        # Extract messages using the architecture handler
        new_messages: list[BaseMessage] = []
        extracted_messages = architecture.extract_messages(chunk_data)
        
        for msg in extracted_messages:
            msg_id = msg.id
            if msg_id not in messages or messages[msg_id] != msg:
                messages[msg_id] = msg
                new_messages.append(msg)
                
        return new_messages

async def astream_state(
    app: Runnable,
    input: Union[Sequence[AnyMessage], Dict[str, Any]],
    config: RunnableConfig,
) -> MessagesStream:
    """Stream messages from the runnable."""
    root_run_id: Optional[str] = None
    messages: dict[str, BaseMessage] = {}
    processor = StreamProcessor()
    
    async for event in app.astream_events(
        input, config, version="v1", stream_mode="values", exclude_tags=["nostream"]
    ):
        try:
            if event["event"] == "on_chain_start" and not root_run_id:
                root_run_id = event["run_id"]
                yield {
                    "run_id": root_run_id,
                    "thread_id": config["configurable"].get("thread_id"),
                }
                
            elif event["event"] == "on_chain_stream" and event["run_id"] == root_run_id:
                new_messages = processor.process_chunk(event, config, messages)
                if new_messages:
                    yield new_messages
                    
            elif event["event"] == "on_chat_model_stream":
                message: BaseMessage = event["data"]["chunk"]
                if message.id not in messages:
                    messages[message.id] = message
                else:
                    messages[message.id] += message
                yield [messages[message.id]]
                
        except Exception as e:
            logger.exception(
                "Error processing stream event",
                error=str(e),
                event_type=event.get("event"),
                exc_info=True
            )
            continue


def _default(obj) -> Any:
    if hasattr(obj, "dict") and callable(obj.dict):
        return obj.dict()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


dumps = functools.partial(orjson.dumps, default=_default)


async def to_sse(messages_stream: MessagesStream) -> AsyncIterator[dict]:
    """Consume the stream into an EventSourceResponse."""
    try:
        async for chunk in messages_stream:
            if isinstance(chunk, dict) and "run_id" in chunk:
                yield {
                    "event": "metadata",
                    "data": orjson.dumps(chunk).decode(),
                }
            elif isinstance(chunk, list):
                yield {
                    "event": "data",
                    "data": dumps(
                        [message_chunk_to_message(msg) for msg in chunk]
                    ).decode(),
                }
    except Exception as e:
        logger.exception(f"error in stream: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": orjson.dumps(
                {"status_code": 500, "message": f"Internal Server Error: {e}"}
            ).decode(),
        }

    yield {"event": "end"}



async def ingest_task_event_generator(task_id: str, redis_service: RedisService):
    """Generator function to stream data ingestion task events to the
    client."""
    logger.info(f"Starting event generator for ingestion {task_id}")
    last_index = 0
    try:
        yield {
            "event": "metadata",
            "data": orjson.dumps({"task_id": task_id}).decode(),
        }

        while True:
            messages = await redis_service.get_progress_messages(task_id, last_index)
            for message in messages:
                logger.debug(f"Sending progress event: {message}")
                yield {
                    "event": "data",
                    "data": orjson.dumps({"progress": message}).decode(),
                }
                last_index += 1

            status = await redis_service.get_ingestion_status(task_id)
            if status in ["completed", "failed"]:
                logger.debug(f"Sending completion event: {status}")
                yield {
                    "event": "data",
                    "data": orjson.dumps({"status": status}).decode(),
                }
                break

            if not messages:
                await asyncio.sleep(0.5)  # Wait a bit before checking again
    except Exception as e:
        logger.exception(f"Error in event generator: {str(e)}")
        yield {
            "event": "error",
            "data": orjson.dumps(
                {"status_code": 500, "message": f"Internal Server Error: {str(e)}"}
            ).decode(),
        }
    finally:
        logger.info(f"Event generator for ingestion {task_id} finished")
        yield {"event": "end"}
