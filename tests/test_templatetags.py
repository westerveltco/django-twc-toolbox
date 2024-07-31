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

from django_twc_toolbox.templatetags.django_twc_toolbox import class_name
from django_twc_toolbox.templatetags.django_twc_toolbox import display_name
from django_twc_toolbox.templatetags.django_twc_toolbox import elided_page_range
from django_twc_toolbox.templatetags.django_twc_toolbox import initials
from django_twc_toolbox.templatetags.django_twc_toolbox import klass
from django_twc_toolbox.templatetags.django_twc_toolbox import query_string
from django_twc_toolbox.templatetags.django_twc_toolbox import startswith

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.mark.parametrize(
    "model,kwargs,expected",
    [
        (User, {"username": "johndoe", "first_name": "John", "last_name": "Doe"}, "JD"),
        (User, {"username": "janedoe"}, "J"),
        (AnonymousUser, {}, "N/A"),
    ],
)
def test_initials(model, kwargs, expected):
    user = model(**kwargs)

    assert initials(user) == expected


@pytest.mark.parametrize(
    "model,kwargs,expected",
    [
        (User, {"username": "johndoe", "first_name": "John", "last_name": "Doe"}, "JD"),
        (User, {"username": "janedoe"}, "J"),
        (AnonymousUser, {}, "N/A"),
    ],
)
def test_initials_templatetag(model, kwargs, expected):
    if kwargs:
        user = baker.make(model, **kwargs)
    else:
        user = model()

    template = Template("{% load django_twc_toolbox %} Initials: {{ user|initials }}")

    rendered = template.render(Context({"user": user}))

    assert f"Initials: {expected}" in rendered


@pytest.mark.parametrize(
    "model,kwargs,expected",
    [
        (
            User,
            {"username": "johndoe", "first_name": "John", "last_name": "Doe"},
            "John Doe",
        ),
        (User, {"username": "janedoe", "first_name": "Jane"}, "Jane"),
        (User, {"username": "bobsmith"}, "Bobsmith"),
        (AnonymousUser, {}, "N/A"),
    ],
)
def test_display_name(model, kwargs, expected):
    user = model(**kwargs)

    assert display_name(user) == expected


@pytest.mark.parametrize(
    "model,kwargs,expected",
    [
        (
            User,
            {"username": "johndoe", "first_name": "John", "last_name": "Doe"},
            "John Doe",
        ),
        (User, {"username": "janedoe", "first_name": "Jane"}, "Jane"),
        (User, {"username": "bobsmith"}, "Bobsmith"),
        (AnonymousUser, {}, "N/A"),
    ],
)
def test_display_name_templatetag(model, kwargs, expected):
    if kwargs:
        user = baker.make(model, **kwargs)
    else:
        user = model()

    template = Template("{% load django_twc_toolbox %} Name: {{ user|display_name }}")

    rendered = template.render(Context({"user": user}))

    assert f"Name: {expected}" in rendered


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
        ("/test/?page=2&sort=name", {"sort": None}, "?page=2"),
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


@pytest.mark.parametrize(
    "url,params,expected",
    [
        (
            "/test/?page=2&sort=name",
            {"foo": "bar"},
            "?page=2&amp;sort=name&amp;foo=bar",
        ),
        ("/test/?page=2&sort=name", {"page": 3}, "?page=3&amp;sort=name"),
        ("/test/?page=2&sort=name", {"sort": None}, "?page=2"),
        ("/test/?page=2&sort=name", {"page": None, "sort": None}, ""),
    ],
)
def test_query_string_templatetag(url, params, expected, rf):
    request = rf.get(url)

    param_string = " ".join(
        [
            f"{key}='{value}'" if value is not None else f"{key}=None"
            for key, value in params.items()
        ]
    )
    template = Template(
        f"{{% load django_twc_toolbox %}} Query: {{% query_string {param_string} %}}"
    )

    rendered = template.render(RequestContext(request, params))

    assert f"Query: {expected}" in rendered


def test_klass():
    template = Template("")

    result = klass(template)

    assert result == Template


def test_klass_templatetag():
    template = Template("{% load django_twc_toolbox %} {{ template|klass }}")

    rendered = template.render(Context({"template": template}))

    assert "django.template.base.Template" in rendered


def test_class_name():
    template = Template("")

    result = class_name(template)

    assert result == "Template"


def test_class_name_templatetag():
    template = Template("{% load django_twc_toolbox %} {{ template|class_name }}")

    rendered = template.render(Context({"template": template}))

    assert "Template" in rendered


def test_startswith():
    assert startswith("FooBar", "Foo")


def test_startswith_templatetag():
    template = Template(
        "{% load django_twc_toolbox %} {% if var|startswith:'Foo' %}Bar{% endif %}"
    )

    rendered = template.render(Context({"var": "FooBar"}))

    assert "Bar" in rendered
