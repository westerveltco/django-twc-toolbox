from __future__ import annotations

import pytest
from django.contrib import admin
from model_bakery import baker

from django_twc_toolbox.admin import ReadOnlyStackedInline
from django_twc_toolbox.admin import ReadOnlyTabularInline

from .dummy.models import Child
from .dummy.models import Parent

pytestmark = pytest.mark.django_db


class ChildStackedInline(ReadOnlyStackedInline[Child, Parent]):
    model = Child
    fk_name = "parent"
    fields = ["bar"]


class ChildTabularInline(ReadOnlyTabularInline[Child, Parent]):
    model = Child
    fk_name = "parent"
    fields = ["bar"]


@pytest.mark.parametrize("inline_class", [ChildStackedInline, ChildTabularInline])
class TestReadOnlyInline:
    def test_inline_configuration(self, inline_class):
        inline = inline_class(Parent, admin.site)

        assert inline.model == Child
        assert inline.fk_name == "parent"
        assert inline.fields == ["bar"]

    def test_readonly_fields(self, rf, admin_user, inline_class):
        request = rf.get("/")
        request.user = admin_user

        inline = inline_class(Parent, admin.site)
        readonly_fields = inline.get_readonly_fields(request)

        assert set(inline.fields).issubset(readonly_fields)

    def test_inline_permissions(self, rf, admin_user, inline_class):
        request = rf.get("/")
        request.user = admin_user

        inline = inline_class(Parent, admin.site)
        parent = baker.make("dummy.Parent")

        assert inline.has_add_permission(request, parent) is False
        assert inline.has_change_permission(request, parent) is False
        assert inline.can_delete is False
        assert inline.extra == 0

    def test_fields_subset_of_model_fields(self, inline_class):
        inline = inline_class(Parent, admin.site)
        model_fields = set(f.name for f in Child._meta.fields)

        assert set(inline.fields).issubset(model_fields)
