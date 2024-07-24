from __future__ import annotations

import pytest
from model_bakery import baker
from neapolitan.views import Role

from .models import Bookmark
from .views import BookmarkTableView
from .views import BookmarkView


@pytest.mark.parametrize(
    "klass,expected",
    [
        (BookmarkView, False),
        (BookmarkTableView, True),
    ],
)
def test_rendered_template_table(klass, expected, rf, db):
    view_func = klass.as_view(role=Role.LIST)
    request = rf.get(Role.LIST.maybe_reverse(klass))
    baker.make(Bookmark, _quantity=3)

    response = view_func(request)

    assert response.status_code == 200

    rendered = response.render()
    content = rendered.content.decode()

    assert ("<h1>With Table</h1>" in content) is expected


def test_rendered_partial_template(rf, db):
    view_func = BookmarkView.as_view(role=Role.LIST)
    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))
    request.htmx = True
    baker.make(Bookmark, _quantity=3)

    response = view_func(request)
    rendered = response.render()
    content = rendered.content.decode()

    # this div is just outside where the partial is defined in the default list template
    assert '<div class="sm:flex sm:items-center">' not in content


@pytest.mark.xfail(
    reason="have not figured out how to dynamically change the partial name using `partialdef` templatetag"
)
def test_rendered_partial_template_different_target(rf, db):
    view_func = BookmarkView.as_view(
        role=Role.LIST, list_partial="test_different_target"
    )
    request = rf.get(Role.LIST.maybe_reverse(BookmarkView))
    request.htmx = True
    baker.make(Bookmark, _quantity=3)

    response = view_func(request)
    rendered = response.render()
    content = rendered.content.decode()

    # this div is just outside where the partial is defined in the default list template
    assert '<div class="sm:flex sm:items-center">' not in content
