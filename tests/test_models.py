from __future__ import annotations

import sys
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
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


def test_changed_by_user():
    user = baker.make(get_user_model())

    dummy = baker.make("dummy.ModelWithHistory", changed_by=user)

    assert dummy.changed_by == user
    assert dummy.history.count() == 1
    assert dummy.history.first().history_user == user


def test_change_user():
    user = baker.make(get_user_model())
    another_user = baker.make(get_user_model())

    dummy = baker.make("dummy.ModelWithHistory", changed_by=user)

    assert dummy.changed_by == user
    assert dummy.history.count() == 1

    dummy.changed_by = another_user
    dummy.save()

    assert dummy.changed_by == another_user
    assert dummy.history.count() == 2
    assert dummy.history.first().history_user == another_user


def test_history_user_property():
    user = baker.make(get_user_model())

    dummy = baker.make("dummy.ModelWithHistory", changed_by=user)

    assert dummy._history_user == user


def test_history_user_setter():
    user = baker.make(get_user_model())
    another_user = baker.make(get_user_model())

    dummy = baker.make("dummy.ModelWithHistory", changed_by=user)

    dummy._history_user = another_user
    dummy.save()

    assert dummy.changed_by == another_user
    assert dummy.history.count() == 2
    assert dummy.history.first().history_user == another_user


def test_multiple_changes_with_different_users():
    user = baker.make(get_user_model())
    another_user = baker.make(get_user_model())

    dummy = baker.make("dummy.ModelWithHistory", changed_by=user)

    dummy.name = "Updated by first user"
    dummy.save()

    dummy._history_user = another_user
    dummy.name = "Updated by second user"
    dummy.save()

    assert dummy.history.count() == 3
    historical_records = list(dummy.history.all())
    assert historical_records[0].history_user == another_user
    assert historical_records[1].history_user == user
    assert historical_records[2].history_user == user


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
