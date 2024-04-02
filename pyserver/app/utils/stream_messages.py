from typing import AsyncIterator, Optional, Sequence, Union
import structlog
import orjson
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    AnyMessage,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    FunctionMessage,
    FunctionMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
)
from langchain_core.runnables import Runnable, RunnableConfig
from langserve.serialization import WellKnownLCSerializer

logger = structlog.get_logger()

MessagesStream = AsyncIterator[Union[list[AnyMessage], str]]


async def astream_messages(
    app: Runnable, input: Sequence[AnyMessage], config: RunnableConfig
) -> MessagesStream:
    """Stream messages from the runnable."""
    root_run_id: Optional[str] = None
    last_messages_list: Optional[list[AnyMessage]] = None
    last_stream_run_id: Optional[str] = None
    async for event in app.astream_events(
        input, config, version="v1", output_keys="__root__"
    ):
        if event["event"] == "on_chain_start" and not root_run_id:
            root_run_id = event["run_id"]

            yield root_run_id
        elif event["event"] == "on_chain_stream" and event["run_id"] == root_run_id:
            last_messages_list = event["data"]["chunk"]

            yield last_messages_list
        elif event["event"] == "on_chat_model_start" and last_messages_list is None:
            input_messages_outer = event["data"]["input"].get("messages")
            input_messages = (
                input_messages_outer[0]
                if isinstance(input_messages_outer, list)
                else None
            )
            input_messages = (
                [msg for msg in input_messages if not isinstance(msg, SystemMessage)]
                if input_messages is not None
                else None
            )
            if input_messages and input_messages != last_messages_list:
                last_messages_list = input_messages
                yield last_messages_list
        elif (
            event["event"] == "on_chat_model_stream" and last_messages_list is not None
        ):
            is_new_stream_run = (
                last_stream_run_id is None or last_stream_run_id != event["run_id"]
            )
            is_diff_msg_type = last_messages_list and type(  # noqa: E721
                last_messages_list[-1]
            ) != type(event["data"]["chunk"])
            if is_new_stream_run or is_diff_msg_type:
                last_stream_run_id = event["run_id"]
                last_messages_list.append(event["data"]["chunk"])
            else:
                last_messages_list[-1] = last_messages_list[-1] + event["data"]["chunk"]

            yield last_messages_list

def map_chunk_to_msg(chunk: BaseMessageChunk, serialize: Optional[bool] = False):
    if not isinstance(chunk, BaseMessageChunk):
        return chunk
    args = {k: v for k, v in chunk.__dict__.items() if k != "type"}
    if isinstance(chunk, HumanMessageChunk):
        message = HumanMessage(**args)
    elif isinstance(chunk, AIMessageChunk):
        message = AIMessage(**args)
    elif isinstance(chunk, FunctionMessageChunk):
        message = FunctionMessage(**args)
    elif isinstance(chunk, ChatMessageChunk):
        message = ChatMessage(**args)
    else:
        raise ValueError(f"Unknown chunk type: {chunk}")

    if serialize:
        return {
            "content": message.content,
            "additional_kwargs": message.additional_kwargs,
            "type": message.type,
            "example": message.example,
        }
    else:
        return message

# TODO: Remove langserve dependency
_serializer = WellKnownLCSerializer()

async def to_sse(messages_stream: MessagesStream) -> AsyncIterator[dict]:
    """Consume the stream into an EventSourceResponse"""
    try:
        async for chunk in messages_stream:
            if isinstance(chunk, str):
                yield {
                    "event": "metadata",
                    "data": orjson.dumps({"run_id": chunk}).decode(),
                }
            else:
                yield {
                    "event": "data",
                    "data": _serializer.dumps(
                        [map_chunk_to_msg(msg) for msg in chunk]
                    ).decode(),
                }
    except Exception as e:
        await logger.exception(f"error in stream: {str(e)}", exc_info=True)
        yield {
            "event": "error",
             # Do not expose the error message to the client
            "data": orjson.dumps(
                {"status_code": 500, "message": "Internal Server Error"}
            ).decode(),
        }

    # Send an end event to signal the end of the stream
    yield {"event": "end"}
