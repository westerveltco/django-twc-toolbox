from __future__ import annotations

from django_filters import BaseInFilter
from django_filters import NumberFilter


class NumberInFilter(BaseInFilter, NumberFilter):
    pass
