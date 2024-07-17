from __future__ import annotations

from typing import Any  # pyright: ignore[reportAny]
from typing import Generic
from typing import TypeVar
from typing import cast

from django.db.models import Model
from django.db.models import QuerySet
from ninja import ModelSchema

_T = TypeVar("_T", bound=ModelSchema)
_M = TypeVar("_M", bound=Model)


class QuerySetModelSchemaMixin(Generic[_T, _M]):
    @classmethod
    def from_queryset(cls: Any, queryset: QuerySet[_M]) -> list[_T]:  # pyright: ignore[reportAny]
        schema_cls = cast(type[_T], cls)
        return [schema_cls.from_orm(obj) for obj in queryset.iterator()]
