from __future__ import annotations

import sys
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import override_settings
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_with_history():
    dummy = baker.make("dummy.ModelWithHistory")

    assert dummy.history.count() == 1


def test_save_without_history_kwarg():
    dummy = baker.make("dummy.ModelWithHistory")

    assert dummy.history.count() == 1

    dummy.name = "New name"
    dummy.save(without_history=True)

    assert dummy.history.count() == 1

    dummy.name = "I'm not a dummy"
    dummy.save()

    assert dummy.history.count() == 2


def test_save_without_history_method():
    dummy = baker.make("dummy.ModelWithHistory")

    assert dummy.history.count() == 1

    dummy.name = "You're a dummy"
    dummy.save_without_history()

    assert dummy.history.count() == 1


@override_settings(
    INSTALLED_APPS=[app for app in settings.INSTALLED_APPS if app != "simple_history"]
)
def test_without_simple_history():
    if "django_twc_toolbox.models" in sys.modules:
        del sys.modules["django_twc_toolbox.models"]

    with patch("importlib.util.find_spec", return_value=None):
        import django_twc_toolbox.models

        assert not hasattr(django_twc_toolbox.models, "WithHistory")

        assert hasattr(django_twc_toolbox.models, "TimeStamped")

    if "django_twc_toolbox.models" in sys.modules:
        del sys.modules["django_twc_toolbox.models"]
