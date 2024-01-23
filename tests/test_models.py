from __future__ import annotations

import pytest

from .models import TestModel


@pytest.mark.django_db
class TestTimeStamped:
    def test_created_at(self):
        obj = TestModel.objects.create()

        assert obj.created_at is not None

    def test_updated_at(self):
        obj = TestModel.objects.create()

        assert obj.updated_at == obj.created_at

        obj.test_field = "updated"
        obj.save()

        assert obj.updated_at > obj.created_at

    def test_update_fields(self):
        obj = TestModel.objects.create()

        assert obj.updated_at == obj.created_at

        obj.test_field = "updated"
        obj.save(update_fields=["test_field"])

        assert obj.updated_at > obj.created_at

    def test_is_edited(self):
        obj = TestModel.objects.create()

        assert not obj.is_edited()

        obj.test_field = "updated"
        obj.save()

        assert obj.is_edited()
