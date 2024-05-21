from __future__ import annotations

import pytest
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
