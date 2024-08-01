from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from ._typing import override

DJANGO_TWC_TOOLBOX_SETTINGS_NAME = "DJANGO_TWC_TOOLBOX"


@dataclass(frozen=True)
class AppSettings:
    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, DJANGO_TWC_TOOLBOX_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))  # pyright: ignore[reportAny]


app_settings = AppSettings()
