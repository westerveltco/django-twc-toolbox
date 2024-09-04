from __future__ import annotations

from typing import Callable
from urllib.parse import urlparse
from urllib.parse import urlunparse

from django.http import HttpRequest
from django.http import HttpResponsePermanentRedirect
from django.http.response import HttpResponseBase


class WwwRedirectMiddleware:
    # all credit to Adam Johnson for the inspiration
    # https://adamj.eu/tech/2020/03/02/how-to-make-django-redirect-www-to-your-bare-domain/

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        url = urlparse(request.build_absolute_uri())

        if url.netloc.startswith("www."):
            bare_netloc = url.netloc.replace("www.", "", 1)
            bare_url_parts = url._replace(netloc=bare_netloc)
            bare_url = urlunparse(bare_url_parts)
            return HttpResponsePermanentRedirect(bare_url)

        return self.get_response(request)
