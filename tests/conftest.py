from __future__ import annotations

import logging
from pathlib import Path

import pytest
from django.conf import settings
from django.http import HttpRequest

from .settings import DEFAULT_SETTINGS

pytest_plugins = []  # type: ignore


def pytest_configure(config):
    logging.disable(logging.CRITICAL)

    settings.configure(**DEFAULT_SETTINGS, **TEST_SETTINGS)


TEST_SETTINGS = {
    "INSTALLED_APPS": [
        "django_twc_toolbox",
        "django_twc_toolbox.crud",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django_tables2",
        "simple_history",
        "template_partials",
        "tests.dummy",
        "tests.test_crud",
    ],
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [Path(__file__).parent / "templates"],
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                ],
                "loaders": [
                    (
                        "template_partials.loader.Loader",
                        [
                            "django.template.loaders.filesystem.Loader",
                            "django.template.loaders.app_directories.Loader",
                        ],
                    )
                ],
            },
        }
    ],
}


@pytest.fixture
def req():
    return HttpRequest()
