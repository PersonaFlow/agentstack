from redis.asyncio import Redis
import structlog
from typing import Optional

logger = structlog.get_logger()


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_progress_messages(self, task_id: str, start_index: int = 0) -> list[str]:
        messages = await self.redis.lrange(f"ingestion:{task_id}:progress", start_index, -1)
        return [message.decode("utf-8") for message in messages]

    async def get_ingestion_status(self, task_id: str) -> Optional[str]:
        status = await self.redis.get(f"ingestion:{task_id}:status")
        if status:
            return status.decode("utf-8")
        return None

    async def push_progress_message(self, task_id: str, message: str):
        await self.redis.rpush(f"ingestion:{task_id}:progress", message)

    async def set_ingestion_status(self, task_id: str, status: str):
        await self.redis.set(f"ingestion:{task_id}:status", status)


async def get_redis_service() -> RedisService:
    from stack.app.core.datastore import get_redis_connection

    redis = await get_redis_connection()
    return RedisService(redis)
