from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import TypeVar
from urllib.parse import urlparse

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


def req(url: str) -> Callable[..., Any]:
    """
    A decorator that sends a HTTP request to the specified endpoint after the
    decorated function has been called. This is useful for health checks on
    periodic tasks.

    Args:
        url: The URL of the endpoint to send the request to.

    Returns:
        The decorated function.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        msg = f"Invalid URL: {url}"
        logger.error(msg)

    def decorator(func: Callable[..., T]) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)

            if not settings.DEBUG:
                httpx.get(url, timeout=5)

            return result

        return inner

    return decorator
