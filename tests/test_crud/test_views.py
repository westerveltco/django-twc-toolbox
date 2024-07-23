from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from model_bakery import baker
from neapolitan.views import Role

from .models import Bookmark
from .views import BookmarkView


def test_get_context_data_no_object():
    context = BookmarkView().get_context_data()

    assert "list_view_url" in context.keys()
    assert "delete_view_url" not in context.keys()
    assert "detail_view_url" not in context.keys()
    assert "update_view_url" not in context.keys()


def test_get_context_data_with_object(db):
    bookmark = baker.make(Bookmark)

    context = BookmarkView(object=bookmark).get_context_data()

    assert "list_view_url" in context.keys()
    assert "delete_view_url" in context.keys()
    assert "detail_view_url" in context.keys()
    assert "update_view_url" in context.keys()


@pytest.mark.parametrize(
    "role,expected",
    [
        (Role.DETAIL, ["url", "title"]),
        (Role.LIST, ["url"]),
        (Role.CREATE, ["url", "title", "note"]),
        (Role.UPDATE, ["url", "title", "note"]),
        (Role.DELETE, ["url", "title", "note"]),
    ],
)
def test_get_fields(role, expected):
    fields = BookmarkView(role=role).get_fields()

    assert fields == expected


@pytest.mark.parametrize(
    "role",
    [
        Role.DETAIL,
        Role.LIST,
        Role.CREATE,
        Role.UPDATE,
        Role.DELETE,
    ],
)
def test_get_fields_only(role):
    fields = BookmarkView(role=role, detail_fields=None, list_fields=None).get_fields()

    assert fields == BookmarkView.fields


@pytest.mark.parametrize(
    "role",
    [
        Role.DETAIL,
        Role.LIST,
        Role.CREATE,
        Role.UPDATE,
        Role.DELETE,
    ],
)
def test_get_fields_override(role):
    class BookmarkViewGetFieldsOverride(BookmarkView):
        def get_fields(self):
            return BookmarkView.fields

    fields = BookmarkViewGetFieldsOverride(
        role=role, fields=None, detail_fields=None, list_fields=None
    ).get_fields()

    assert fields == BookmarkView.fields


@pytest.mark.parametrize(
    "role",
    [
        Role.DETAIL,
        Role.LIST,
        Role.CREATE,
        Role.UPDATE,
        Role.DELETE,
    ],
)
def test_get_fields_no_fields(role):
    with pytest.raises(ImproperlyConfigured):
        BookmarkView(
            role=role, fields=None, detail_fields=None, list_fields=None
        ).get_fields()


def test_get_detail_fields():
    fields = BookmarkView().get_detail_fields()

    assert fields != BookmarkView.fields
    assert fields == BookmarkView.detail_fields


def test_get_detail_fields_override():
    class BookmarkViewGetDetailFieldsOverride(BookmarkView):
        def get_detail_fields(self):
            return BookmarkView.fields

    fields = BookmarkViewGetDetailFieldsOverride().get_detail_fields()

    assert fields == BookmarkView.fields
    assert fields != BookmarkView.detail_fields


def test_get_list_fields():
    fields = BookmarkView().get_list_fields()

    assert fields != BookmarkView.fields
    assert fields == BookmarkView.list_fields


def test_get_list_fields_override():
    class BookmarkViewGetListFieldsOverride(BookmarkView):
        def get_list_fields(self):
            return BookmarkView.fields

    fields = BookmarkViewGetListFieldsOverride().get_list_fields()

    assert fields == BookmarkView.fields
    assert fields != BookmarkView.list_fields
