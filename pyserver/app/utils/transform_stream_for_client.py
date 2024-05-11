import json
from typing import AsyncIterator
from fastapi.encoders import jsonable_encoder


async def transform_stream_for_client(
    stream: AsyncIterator,
) -> AsyncIterator[str]:
    async for chunk in stream:
        yield f"event: data\ndata: {json.dumps(jsonable_encoder(chunk))}\n\n"
    yield "event: end\n\n"
