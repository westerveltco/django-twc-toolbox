from __future__ import annotations

from typing import TYPE_CHECKING

from django_twc_toolbox.conf import app_settings

if TYPE_CHECKING:
    from sentry_sdk._types import SamplingContext


def sentry_traces_sampler(sampling_context: SamplingContext):
    if _should_disgard(sampling_context):
        return 0

    return app_settings.SENTRY_TRACES_RATE


def sentry_profiles_sampler(sampling_context: SamplingContext):
    if _should_disgard(sampling_context):
        return 0

    return app_settings.SENTRY_PROFILE_RATE


def _should_disgard(sampling_context: SamplingContext) -> bool:
    DISGARDED_METHODS = app_settings.SENTRY_DISGARDED_METHODS
    DISGARDED_PATHS = app_settings.SENTRY_DISGARDED_PATHS

    return (
        sampling_context.get("wsgi_environ", None) is not None
        and sampling_context["wsgi_environ"]["REQUEST_METHOD"] in DISGARDED_METHODS
        and sampling_context["wsgi_environ"]["PATH_INFO"] in DISGARDED_PATHS
    )
