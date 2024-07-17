from __future__ import annotations

import pytest
from django.test import override_settings

from django_twc_toolbox.conf import app_settings
from django_twc_toolbox.sentry import _should_disgard
from django_twc_toolbox.sentry import sentry_profiles_sampler
from django_twc_toolbox.sentry import sentry_traces_sampler


@pytest.fixture
def sample_context():
    return {"wsgi_environ": {"REQUEST_METHOD": "GET", "PATH_INFO": "/health/"}}


@pytest.fixture
def non_discard_context():
    return {"wsgi_environ": {"REQUEST_METHOD": "POST", "PATH_INFO": "/api/data/"}}


def test_sentry_traces_sampler_discard(sample_context):
    assert sentry_traces_sampler(sample_context) == 0


def test_sentry_traces_sampler_non_discard(non_discard_context):
    assert sentry_traces_sampler(non_discard_context) == app_settings.SENTRY_TRACES_RATE


def test_sentry_profiles_sampler_discard(sample_context):
    assert sentry_profiles_sampler(sample_context) == 0


def test_sentry_profiles_sampler_non_discard(non_discard_context):
    assert (
        sentry_profiles_sampler(non_discard_context) == app_settings.SENTRY_PROFILE_RATE
    )


def test_should_discard(sample_context):
    assert _should_disgard(sample_context) is True


def test_should_not_discard(non_discard_context):
    assert _should_disgard(non_discard_context) is False


def test_should_discard_empty_context():
    assert _should_disgard({}) is False


@override_settings(
    DJANGO_TWC_TOOLBOX={
        "SENTRY_DISGARDED_METHODS": ["POST"],
        "SENTRY_DISGARDED_PATHS": ["/api/"],
        "SENTRY_TRACES_RATE": 0.75,
        "SENTRY_PROFILE_RATE": 0.25,
    }
)
def test_custom_settings():
    context = {"wsgi_environ": {"REQUEST_METHOD": "POST", "PATH_INFO": "/api/"}}

    assert _should_disgard(context) is True
    assert (
        sentry_traces_sampler(
            {"wsgi_environ": {"REQUEST_METHOD": "GET", "PATH_INFO": "/other/"}}
        )
        == 0.75
    )
    assert (
        sentry_profiles_sampler(
            {"wsgi_environ": {"REQUEST_METHOD": "GET", "PATH_INFO": "/other/"}}
        )
        == 0.25
    )


@pytest.mark.parametrize(
    "method,path,expected",
    [
        ("GET", "/health/", True),
        ("HEAD", "/health/", True),
        ("POST", "/health/", False),
        ("GET", "/api/", False),
        ("HEAD", "/api/", False),
    ],
)
def test_should_discard_parametrized(method, path, expected):
    context = {"wsgi_environ": {"REQUEST_METHOD": method, "PATH_INFO": path}}

    assert _should_disgard(context) == expected
