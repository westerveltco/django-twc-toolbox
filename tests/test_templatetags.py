from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.http import QueryDict
from django.template import Context
from django.template import RequestContext
from django.template import Template
from model_bakery import baker

from django_twc_toolbox.templatetags.django_twc_toolbox import display_name
from django_twc_toolbox.templatetags.django_twc_toolbox import elided_page_range
from django_twc_toolbox.templatetags.django_twc_toolbox import initials
from django_twc_toolbox.templatetags.django_twc_toolbox import query_string

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_initials():
    user = User(username="johndoe", first_name="John", last_name="Doe")
    assert initials(user) == "JD"

    user = User(username="janedoe")
    assert initials(user) == "J"

    anonymous_user = AnonymousUser()
    assert initials(anonymous_user) == "N/A"


def test_initials_templatetag():
    user = baker.make(User, username="testuser", first_name="Test", last_name="User")

    template = Template("{% load django_twc_toolbox %} Initials: {{ user|initials }}")

    rendered = template.render(Context({"user": user}))

    assert "Initials: TU" in rendered


def test_display_name():
    user = User(username="johndoe", first_name="John", last_name="Doe")
    assert display_name(user) == "John Doe"

    user = User(username="janedoe", first_name="Jane")
    assert display_name(user) == "Jane"

    user = User(username="bobsmith")
    assert display_name(user) == "Bobsmith"

    anonymous_user = AnonymousUser()
    assert display_name(anonymous_user) == "N/A"


def test_display_name_templatetag():
    user = baker.make(User, username="testuser", first_name="Test", last_name="User")

    template = Template("{% load django_twc_toolbox %} Name: {{ user|display_name }}")

    rendered = template.render(Context({"user": user}))

    assert "Name: Test User" in rendered


@pytest.mark.parametrize(
    "object_count,per_page,page,expected",
    [
        (101, 5, 1, [1, 2, 3, 4, Paginator.ELLIPSIS, 20, 21]),
        (
            101,
            5,
            10,
            [
                1,
                2,
                Paginator.ELLIPSIS,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                Paginator.ELLIPSIS,
                20,
                21,
            ],
        ),
        (101, 5, 21, [1, 2, Paginator.ELLIPSIS, 18, 19, 20, 21]),
    ],
)
def test_elided_page_range(object_count, per_page, page, expected):
    objects = range(object_count)
    paginator = Paginator(objects, per_page=per_page)
    page_obj = paginator.page(page)

    result = list(elided_page_range(page_obj))
    assert result == expected


@pytest.mark.parametrize(
    "object_count,per_page,page,expected",
    [
        (101, 5, 1, f"Pages: 1 2 3 4 {Paginator.ELLIPSIS} 19 20"),
        (
            101,
            5,
            10,
            f"Pages: 1 2 {Paginator.ELLIPSIS} 7 8 9 10 11 12 13 {Paginator.ELLIPSIS} 19 20",
        ),
        (101, 5, 20, f"Pages: 1 2 {Paginator.ELLIPSIS} 17 18 19 20"),
    ],
)
def test_elided_page_range_templatetag(object_count, per_page, page, expected):
    objects = range(1, object_count)
    paginator = Paginator(objects, per_page=per_page)
    page_obj = paginator.page(page)

    template = Template(
        "{% load django_twc_toolbox %} {% elided_page_range page_obj as range %} Pages: {% for p in range %}{{ p }} {% endfor %}"
    )

    rendered = template.render(Context({"page_obj": page_obj}))

    assert expected in rendered


@pytest.mark.parametrize(
    "url,params,expected",
    [
        ("/test/?page=2&sort=name", {"foo": "bar"}, "?page=2&sort=name&foo=bar"),
        ("/test/?page=2&sort=name", {"page": 3}, "?page=3&sort=name"),
        ("/test/?page=2&sort=name", {"sort": None}, "?page=3"),
        ("/test/?page=2&sort=name", {"page": None, "sort": None}, ""),
    ],
)
def test_query_string(url, params, expected, rf):
    request = rf.get(url)

    result = query_string(RequestContext(request), **params)

    assert result == expected


def test_query_string_querydict(rf):
    request = rf.get("/test/?page=2&sort=name")
    custom_query = QueryDict("a=1&b=2&c=3", mutable=True)

    result = query_string(RequestContext(request), custom_query, b="new", d="added")

    assert result == "?a=1&b=new&c=3&d=added"


def test_query_string_templatetag(rf):
    request = rf.get("test/?filter=active")

    template = Template(
        "{% load django_twc_toolbox %} Query: {% query_string page=3 sort='name' %}"
    )

    rendered = template.render(RequestContext(request))

    assert "Query: ?filter=active&page=3&sort=name" in rendered
