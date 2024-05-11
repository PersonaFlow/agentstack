import redis

from .cache import create_redis

pool = create_redis()


def get_redis():
    """Get instance of redis reusing the connection pool to avoid constantly
    opening/closing connections, yet get a fresh instance of redis each
    time."""
    return redis.Redis(connection_pool=pool)
