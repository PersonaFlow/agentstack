import os

import redis

"""
GLOBALS
"""
REDIS_SSL = os.environ.get("REDIS_SSL") == "1"
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")


def create_redis():
    """Create Redis connection pool to use through the lifetime of the
    service."""
    return redis.ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        connection_class=redis.SSLConnection if REDIS_SSL else redis.Connection,
        decode_responses=True,
    )
