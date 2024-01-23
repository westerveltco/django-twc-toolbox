from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING
from typing import TypeVar
from urllib.parse import urlparse

import pytest_is_running
import urllib3
from django.conf import settings
from django.core.cache import caches

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


T = TypeVar("T")


def hc(url: str) -> Callable[..., T]:
    """
    A decorator that sends a HTTP request to the specified healthcheck endpoint
    if the url argument is provided.

    Args:
        url: The health check endpoint to send a HTTP request to.

    Returns:
        The decorated function.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {url}")

    def decorator(func: Callable[..., T]) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)

            # send a HTTP request to the health check endpoint, if provided
            # don't send a request if in STAGING or when running tests
            if not settings.STAGING and not pytest_is_running.is_running():
                http = urllib3.PoolManager()
                http.request("GET", url)

            return result

        return inner

    return decorator


def cache_func_result(cache: str = "default", key: str | None = None, timeout: int | None = None):
    def decorator(func: Callable[..., T]) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> T:
            nonlocal cache, key, timeout

            cache = caches[cache]

            if key is None:
                key = func.__name__
            if timeout is None:
                timeout = settings.CACHES[cache].get("TIMEOUT", 0)

            if cache.get(key):
                return cache.get(key)

            data = func(*args, **kwargs)
            cache.set(key, data, timeout)

            return data

        return inner

    return decorator
