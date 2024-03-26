from functools import lru_cache

from redis.asyncio import Redis

from heavy_stack.config import get_config


@lru_cache(1)
def redis_client() -> Redis:
    config = get_config()
    return Redis.from_url(config.REDIS_URL)
