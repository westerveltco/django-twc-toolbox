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


class req:
    """
    A decorator that sends a HTTP request to the specified endpoint after the
    decorated function has been called. This is useful for health checks on
    periodic tasks or dispatching webhooks.

    Args:
        url: The URL of the endpoint to send the request to.

    Returns:
        The decorated function.
    """
    def __init__(self, url: str, *, client: httpx.Client | None = None) -> None:
        self.url = url
        self.client = client or httpx.Client()

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        parsed_url = urlparse(self.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            msg = f"Invalid URL: {self.url}"
            logger.error(msg)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Execute the decorated function
            result = func(*args, **kwargs)

            # Send the HTTP request if not in DEBUG mode
            if not settings.DEBUG:
                self.client.get(self.url)

            return result

        return wrapper
