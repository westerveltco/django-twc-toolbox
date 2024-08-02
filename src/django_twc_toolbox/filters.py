from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django_filters import BaseInFilter
from django_filters import Filter
from django_filters import NumberFilter


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class SearchFilter(Filter):
    def __init__(self, *args, search_fields=None, **kwargs):
        if search_fields is None:
            raise ImproperlyConfigured("The 'search_fields' argument is required.")
        self.search_fields = search_fields
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        value = value.strip().split(" ")

        q = Q()
        for field in self.search_fields:
            for term in value:
                q |= Q(**{field + "__icontains": term})
        return qs.filter(q)
