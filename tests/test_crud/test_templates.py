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

    print(f"{content=}")
    assert ('<div class="flow-root mt-8"' in content) is expected
