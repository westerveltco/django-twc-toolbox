from __future__ import annotations

import sys
from typing import Generic
from typing import TypeVar

from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.db.models.base import Model
from django.http import HttpRequest

if sys.version_info >= (3, 9):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

_K = TypeVar("_K")
_ListOrTuple: TypeAlias = list[_K] | tuple[_K, ...] | tuple[()]
_ChildModelT = TypeVar("_ChildModelT", bound=Model)
_ParentModelT = TypeVar("_ParentModelT", bound=Model)


class ReadOnlyModelAdmin(
    Generic[_ChildModelT, _ParentModelT], BaseModelAdmin[_ChildModelT]
):
    can_delete = False
    extra = 0

    @override
    def get_readonly_fields(
        self, request: HttpRequest, obj: _ChildModelT | None = None
    ) -> _ListOrTuple[str]:
        return [f.name for f in self.model._meta.fields]

    @override
    def has_add_permission(  # type: ignore[override]
        self, request: HttpRequest, obj: _ParentModelT | None
    ) -> bool:
        return False

    @override
    def has_change_permission(  # type: ignore[override]
        self, request: HttpRequest, obj: _ParentModelT | None = None
    ) -> bool:
        return False


class ReadOnlyStackedInline(
    ReadOnlyModelAdmin[_ChildModelT, _ParentModelT],
    admin.StackedInline[_ChildModelT, _ParentModelT],
): ...


class ReadOnlyTabularInline(
    ReadOnlyModelAdmin[_ChildModelT, _ParentModelT],
    admin.TabularInline[_ChildModelT, _ParentModelT],
): ...
