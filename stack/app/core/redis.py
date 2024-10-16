from redis.asyncio import Redis
import structlog
from typing import Optional

logger = structlog.get_logger()


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_progress_message(self, ingestion_id: str) -> Optional[str]:
        message = await self.redis.lpop(f"ingestion:{ingestion_id}:progress")
        if message:
            return message.decode("utf-8")
        return None

    async def get_ingestion_status(self, ingestion_id: str) -> Optional[str]:
        status = await self.redis.get(f"ingestion:{ingestion_id}:status")
        if status:
            return status.decode("utf-8")
        return None

    async def push_progress_message(self, ingestion_id: str, message: str):
        await self.redis.rpush(f"ingestion:{ingestion_id}:progress", message)

    async def set_ingestion_status(self, ingestion_id: str, status: str):
        await self.redis.set(f"ingestion:{ingestion_id}:status", status)


async def get_redis_service() -> RedisService:
    from stack.app.core.datastore import get_redis_connection

    redis = await get_redis_connection()
    return RedisService(redis)
