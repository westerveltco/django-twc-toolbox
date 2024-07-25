from __future__ import annotations

import pytest
from django.test import override_settings
from django.urls import NoReverseMatch
from django.urls import path

from django_twc_toolbox.urls import reverse


def view(request):
    return "Hello World"


def view_with_arg(request, arg):
    return arg


urlpatterns = [
    path("view/", view, name="view"),
    path("view_with_arg/<int:arg>/", view_with_arg, name="view_with_arg"),
]


@pytest.fixture(autouse=True)
def urlconf():
    with override_settings(ROOT_URLCONF=__name__):
        yield


@pytest.mark.parametrize(
    "viewname,kwargs,query,fragment,expected",
    [
        ("view", None, None, None, "/view/"),
        (view, None, None, None, "/view/"),
        ("view_with_arg", {"arg": 123}, None, None, "/view_with_arg/123/"),
        ("view", None, {"param": "hello"}, None, "/view/?param=hello"),
        ("view", None, None, "fragment", "/view/#fragment"),
        ("view", None, {"param": "hello"}, "fragment", "/view/?param=hello#fragment"),
        (
            "view",
            None,
            {"param": "hello++"},
            "fragment&more",
            "/view/?param=hello%2B%2B#fragment%26more",
        ),
        (
            "view",
            None,
            {"params": ["hello", "world"]},
            None,
            "/view/?params=%5B%27hello%27%2C+%27world%27%5D",
        ),
        ("view", None, {"param": ""}, None, "/view/?param="),
    ],
)
def test_reverse(viewname, kwargs, query, fragment, expected):
    assert reverse(viewname, kwargs=kwargs, query=query, fragment=fragment) == expected


@pytest.mark.parametrize(
    "viewname,kwargs,query,fragment,expected",
    [
        ("view", {"unexpected": "param"}, None, None, NoReverseMatch),
        ("view_with_arg", None, None, None, NoReverseMatch),
        ("view_with_arg", {"arg": "incorrect_type"}, None, None, NoReverseMatch),
        ("view", None, {"param": None}, None, TypeError),
        ("nonexistent_view", None, None, None, NoReverseMatch),
    ],
)
def test_reverse_invalid(viewname, kwargs, query, fragment, expected):
    with pytest.raises(expected):
        reverse(viewname, kwargs=kwargs, query=query, fragment=fragment)
