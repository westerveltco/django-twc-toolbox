from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import TypeVar

from django import template
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Page
from django.core.paginator import Paginator
from django.db import models
from django.utils.itercompat import is_iterable

from django_twc_toolbox.numbers import format_number_no_round

register = template.Library()


@register.filter
def initials(user: AbstractUser) -> str:
    if not hasattr(user, "username") or isinstance(user, AnonymousUser):
        return "N/A"

    initials = user.username[0].upper()

    if user.first_name and user.last_name:
        initials = f"{user.first_name[0].upper()}{user.last_name[0].upper()}"

    return initials


@register.filter
def display_name(user: AbstractUser) -> str:
    if not hasattr(user, "username") or isinstance(user, AnonymousUser):
        return "N/A"

    if user.first_name and user.last_name:
        display_name = f"{user.first_name} {user.last_name}"
    elif user.first_name:
        display_name = user.first_name
    else:
        display_name = user.username

    return display_name.title()


_TModel = TypeVar("_TModel", bound=models.Model)


@register.simple_tag()
def elided_page_range(page_obj: Page[_TModel]) -> Iterable[str | int]:
    paginator: Paginator[_TModel] | None = getattr(page_obj, "paginator", None)
    if not paginator:
        return []
    return paginator.get_elided_page_range(page_obj.number)


# Coming in the next Django version
# Copied from https://github.com/django/django/pull/17368
# TODO: Remove this when Django 5.1 is released
@register.simple_tag(takes_context=True)
def query_string(context, query_dict=None, **kwargs):
    """
    Add, remove, and change parameters of a ``QueryDict`` and return the result
    as a query string. If the ``query_dict`` argument is not provided, default
    to ``request.GET``.
    For example::
        {% query_string foo=3 %}
    To remove a key::
        {% query_string foo=None %}
    To use with pagination::
        {% query_string page=page_obj.next_page_number %}
    A custom ``QueryDict`` can also be used::
        {% query_string my_query_dict foo=3 %}
    """
    if query_dict is None:
        query_dict = context.request.GET
    query_dict = query_dict.copy()
    for key, value in kwargs.items():
        if value is None:
            if key in query_dict:
                del query_dict[key]
        elif is_iterable(value) and not isinstance(value, str):
            query_dict.setlist(key, value)
        else:
            query_dict[key] = value
    if not query_dict:
        return ""
    query_string = query_dict.urlencode()
    return f"?{query_string}"


_T = TypeVar("_T")


@register.filter
def klass(instance: _T) -> type[_T]:
    return instance.__class__


@register.filter
def class_name(instance: object) -> str:
    return instance.__class__.__name__


@register.filter
def startswith(text: str, starts: str) -> bool:
    return text.startswith(starts)


@register.filter
def format_no_round(
    number: float | int | str | Decimal, decimal_places: int = 2
) -> str:
    return str(format_number_no_round(number, decimal_places=decimal_places))
