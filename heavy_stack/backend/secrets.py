from enum import Enum
from typing import cast

import cachetools
import cachetools.func

from heavy_stack.config import get_config
from heavy_stack.env import is_dev

SecretVersion = str
SecretValue = str

config = get_config()


class Secrets(str, Enum):
    DEMO_SECRET = "DEMO_SECRET"


def async_ttl_cache(*cache_args, **cache_kwargs):
    cache = cachetools.TTLCache(*cache_args, **cache_kwargs)

    def decorator(func):
        async def wrapper(*args, **kwargs):
            key = cachetools.keys.hashkey(*args, **kwargs)
            try:
                # Try to get the cached result
                return cache[key]
            except KeyError:
                # If not cached, call the function and cache the result
                result = await func(*args, **kwargs)
                cache[key] = result
                return result

        return wrapper

    return decorator


if is_dev():

    @async_ttl_cache(10, ttl=20)
    async def get_secret(secret_id: Secrets, version_id: str | None = None) -> tuple[SecretVersion, SecretValue]:
        version_id = version_id or "latest"
        vals = {
            Secrets.DEMO_SECRET: {
                "latest": ("2", "second"),
                "2": ("2", "second"),
                "1": ("1", "first"),
            },
        }
        return vals[secret_id][version_id]

else:

    @async_ttl_cache(128, ttl=480)
    async def get_secret(secret_id: Secrets, version_id: str | None = None) -> tuple[SecretVersion, SecretValue]:
        raise NotImplementedError()
