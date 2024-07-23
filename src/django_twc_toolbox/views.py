from __future__ import annotations

from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from .conf import app_settings


def custom_error_404(
    request: HttpRequest,
    exception: Exception | None = None,
    *args: object,
    **kwargs: object,
) -> HttpResponse:
    return render(request, app_settings.TEMPLATE_404, context={}, status=404)


def custom_error_500(
    request: HttpRequest, *args: object, **kwargs: object
) -> HttpResponse:
    return render(request, app_settings.TEMPLATE_500, context={}, status=500)


@require_GET
@cache_control(max_age=app_settings.CACHE_TIME_ROBOTS_TXT, immutable=True, public=True)
def robots_txt(request: HttpRequest) -> HttpResponse:
    return render(request, app_settings.TEMPLATE_ROBOTS_TXT, content_type="text/plain")


@require_GET
@cache_control(
    max_age=app_settings.CACHE_TIME_SECURITY_TXT, immutable=True, public=True
)
def security_txt(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        app_settings.TEMPLATE_SECURITY_TXT,
        context={
            "year": timezone.now().year + 1,
        },
        content_type="text/plain",
    )
