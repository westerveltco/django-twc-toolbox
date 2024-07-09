from __future__ import annotations

from typing import Generic
from typing import TypeVar

from django.contrib import admin
from django.db import models
from django.http import HttpRequest

_ChildModelT = TypeVar("_ChildModelT", bound=models.Model)
_ParentModelT = TypeVar("_ParentModelT", bound=models.Model)


class ReadOnlyInlineMixin(Generic[_ChildModelT, _ParentModelT]):
    can_delete = False
    extra = 0
    model: type[_ChildModelT]  # type: ignore[reportUninitializedInstanceVariable]

    def get_readonly_fields(
        self, request: HttpRequest, obj: _ChildModelT | None = None
    ) -> list[str] | tuple[str]:
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(
        self, request: HttpRequest, obj: _ParentModelT | None
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: _ParentModelT | None = None
    ) -> bool:
        return False


class ReadOnlyStackedInline(
    ReadOnlyInlineMixin[_ChildModelT, _ParentModelT],
    admin.StackedInline[_ChildModelT, _ParentModelT],
): ...


class ReadOnlyTabularInline(
    ReadOnlyInlineMixin[_ChildModelT, _ParentModelT],
    admin.TabularInline[_ChildModelT, _ParentModelT],
): ...
