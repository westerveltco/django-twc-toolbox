from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django_tables2.views import SingleTableMixin
from model_bakery import baker
from neapolitan.views import Role

from .models import Bookmark
from .views import BookmarkTableOrderedView
from .views import BookmarkTableView
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


@pytest.mark.parametrize(
    "klass,expected",
    [
        (BookmarkView, False),
        (BookmarkTableView, True),
    ],
)
def test_as_view_table_class(klass, expected):
    view = klass.as_view(role=Role.LIST)

    assert issubclass(view.view_class, SingleTableMixin) is expected


@pytest.mark.parametrize(
    "klass,expected",
    [
        (BookmarkView, False),
        (BookmarkTableView, True),
    ],
)
def test_get_context_data_table(klass, expected, rf, db):
    View = klass.as_view(role=Role.LIST, object=baker.make(Bookmark)).view_class
    request = rf.get(Role.LIST.maybe_reverse(View))

    context = View(request=request).get_context_data()

    assert ("table" in context.keys()) is expected


@pytest.mark.parametrize(
    "htmx,expected",
    [
        (True, "neapolitan/object_list.html#object-list"),
        (False, "neapolitan/object_list.html"),
    ],
)
def test_get_template_names(htmx, expected, rf):
    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))
    request.htmx = htmx

    view = BookmarkView(role=Role.LIST, **Role.LIST.extra_initkwargs())
    view.setup(request)

    template_names = view.get_template_names()

    assert expected in template_names


def test_get_template_names_no_htmx(rf):
    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))

    view = BookmarkView(role=Role.LIST, **Role.LIST.extra_initkwargs())
    view.setup(request)

    template_names = view.get_template_names()

    assert "neapolitan/object_list.html" in template_names
    assert "neapolitan/object_list.html#object-list" not in template_names


def test_table_view_ordered(client, db):
    baker.make(Bookmark, _quantity=3)

    response = client.get(Role.LIST.maybe_reverse(BookmarkTableOrderedView))

    assert response.status_code == 200


def test_filterset_primary_fields(rf):
    class BookmarkFilterSetPrimaryFieldsView(BookmarkView):
        filterset_fields = ["url", "title", "note"]
        filterset_primary_fields = ["url"]

    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))

    view = BookmarkFilterSetPrimaryFieldsView(
        role=Role.LIST, **Role.LIST.extra_initkwargs()
    )
    view.setup(request)

    filterset = view.get_filterset()

    assert set(filterset.primary_fields) == {"url"}
    assert set(filterset.secondary_fields) == {"title", "note"}


def test_filterset_extra_methods(rf):
    class BookmarkFilterSetExtraMethodsView(BookmarkView):
        filterset_fields = ["url", "title", "note"]

    request = rf.get(
        Role.LIST.maybe_reverse(BookmarkView), data=QueryDict("url=example.com")
    )

    view = BookmarkFilterSetExtraMethodsView(
        role=Role.LIST, **Role.LIST.extra_initkwargs()
    )
    view.setup(request)

    filterset = view.get_filterset()

    filterset.form.is_valid()

    assert hasattr(filterset, "is_active")
    assert hasattr(filterset.__class__, "active_filters")


def test_filterset_is_active(rf):
    class BookmarkFilterSetIsActiveView(BookmarkView):
        filterset_fields = ["url", "title", "note"]

    request = rf.get(
        Role.LIST.maybe_reverse(BookmarkView), data=QueryDict("url=example.com")
    )

    view = BookmarkFilterSetIsActiveView(role=Role.LIST, **Role.LIST.extra_initkwargs())
    view.setup(request)

    filterset = view.get_filterset()

    filterset.form.is_valid()

    assert callable(filterset.is_active)
    assert filterset.is_active() is True


def test_filterset_active_filters(rf):
    class BookmarkFilterSetActiveFiltersView(BookmarkView):
        filterset_fields = ["url", "title", "note"]

    request = rf.get(
        Role.LIST.maybe_reverse(BookmarkView), data=QueryDict("url=example.com")
    )

    view = BookmarkFilterSetActiveFiltersView(
        role=Role.LIST, **Role.LIST.extra_initkwargs()
    )
    view.setup(request)

    filterset = view.get_filterset()

    filterset.form.is_valid()

    assert isinstance(filterset.active_filters, dict)
    assert filterset.active_filters == {"url": "example.com"}


def test_filterset_extra_methods_no_filters(rf):
    class BookmarkFilterSetExtraMethodsView(BookmarkView):
        filterset_fields = ["url", "title", "note"]

    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))

    view = BookmarkFilterSetExtraMethodsView(
        role=Role.LIST, **Role.LIST.extra_initkwargs()
    )
    view.setup(request)

    filterset = view.get_filterset()

    filterset.form.is_valid()

    assert filterset.is_active() is False
    assert filterset.active_filters == {}
