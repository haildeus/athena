import os
from functools import wraps, lru_cache
from typing import Optional, List, Union

from diskcache import Cache
from circuitbreaker import circuit
import orjson

from src.athena.core.system import system_config, logger


def resolve_path(obj, path):
    for part in path:
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
        if obj is None:
            break
    return obj


@circuit(
    failure_threshold=system_config.FAILURE_THRESHOLD,
    recovery_timeout=system_config.RECOVERY_TIMEOUT,
)
@lru_cache(maxsize=1)
def get_disk_cache():
    cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache")
    return Cache(cache_dir)


def diskcache(
    *,
    cache_owner_path: Optional[Union[str, List[str]]] = None,
    cache_params: Optional[List[str]] = None,
    cache_ttl: int = system_config.CACHE_TTL,
):
    """
    Cache decorator using diskcache.
    """
    cache_params = cache_params or []

    if isinstance(cache_owner_path, str):
        owner_paths = [cache_owner_path.split(".")]
    elif isinstance(cache_owner_path, list):
        owner_paths = [
            path.split(".") if isinstance(path, str) else path
            for path in cache_owner_path
        ]
    else:
        owner_paths = []

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [func.__module__, func.__name__]
            disk_cache = get_disk_cache()

            for path in owner_paths:
                if path:
                    cache_owner_property = resolve_path(kwargs.get(path[0]), path[1:])
                    if cache_owner_property:
                        key_parts.append(str(cache_owner_property))

            params = {
                param: kwargs.get(param) for param in cache_params if param in kwargs
            }
            if params:
                result = orjson.dumps(params).decode("utf-8")
                key_parts.append(result)

            key = ":".join(key_parts)

            try:
                # Try to get cached value
                cached_value = disk_cache.get(key)
                if cached_value is not None:
                    if isinstance(cached_value, str) or isinstance(cached_value, dict):
                        try:
                            return orjson.loads(cached_value)
                        except Exception as e:
                            return cached_value

                    return cached_value

                # If not cached, call the function
                response = await func(*args, **kwargs)

                disk_cache.set(key, response, expire=cache_ttl)
                return response

            except Exception as e:
                logger.error(f"Caching error: {str(e)}")
                return await func(*args, **kwargs)

        return wrapper

    return decorator
