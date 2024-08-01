from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from ._typing import override

DJANGO_TWC_TOOLBOX_SETTINGS_NAME = "DJANGO_TWC_TOOLBOX"


@dataclass(frozen=True)
class AppSettings:
    CACHE_TIME_ROBOTS_TXT = 60 * 60 * 24  # one day
    CACHE_TIME_SECURITY_TXT = 60 * 60 * 24  # one day
    TEMPLATE_404 = "404.html"
    TEMPLATE_500 = "500.html"
    TEMPLATE_ROBOTS_TXT = "robots.txt"
    TEMPLATE_SECURITY_TXT = ".well-known/security.txt"
    SENTRY_DISGARDED_METHODS = ["GET", "HEAD"]
    SENTRY_DISGARDED_PATHS = ["/health/"]
    SENTRY_PROFILE_RATE = 0.5
    SENTRY_TRACES_RATE = 0.5

    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, DJANGO_TWC_TOOLBOX_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))  # pyright: ignore[reportAny]


app_settings = AppSettings()
