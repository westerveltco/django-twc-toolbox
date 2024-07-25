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
    "viewname,args,kwargs,query,fragment,expected",
    [
        ("view", None, None, None, None, "/view/"),
        (view, None, None, None, None, "/view/"),
        ("view_with_arg", (123,), None, None, None, "/view_with_arg/123/"),
        ("view_with_arg", None, {"arg": 123}, None, None, "/view_with_arg/123/"),
        ("view", None, None, {"param": "hello"}, None, "/view/?param=hello"),
        ("view", None, None, None, "fragment", "/view/#fragment"),
        (
            "view",
            None,
            None,
            {"param": "hello"},
            "fragment",
            "/view/?param=hello#fragment",
        ),
        (
            "view",
            None,
            None,
            {"param": "hello++"},
            "fragment&more",
            "/view/?param=hello%2B%2B#fragment%26more",
        ),
        (
            "view",
            None,
            None,
            {"params": ["hello", "world"]},
            None,
            "/view/?params=%5B%27hello%27%2C+%27world%27%5D",
        ),
        ("view", None, None, {"param": ""}, None, "/view/?param="),
    ],
)
def test_reverse(viewname, args, kwargs, query, fragment, expected):
    assert (
        reverse(viewname, args=args, kwargs=kwargs, query=query, fragment=fragment)
        == expected
    )


@pytest.mark.parametrize(
    "viewname,args,kwargs,query,fragment,expected",
    [
        ("view", None, {"unexpected": "param"}, None, None, NoReverseMatch),
        ("view_with_arg", None, None, None, None, NoReverseMatch),
        ("view_with_arg", "incorrect_type", None, None, None, NoReverseMatch),
        ("view_with_arg", None, {"arg": "incorrect_type"}, None, None, NoReverseMatch),
        ("view", None, None, {"param": None}, None, TypeError),
        ("nonexistent_view", None, None, None, None, NoReverseMatch),
    ],
)
def test_reverse_invalid(viewname, args, kwargs, query, fragment, expected):
    with pytest.raises(expected):
        reverse(viewname, args=args, kwargs=kwargs, query=query, fragment=fragment)
