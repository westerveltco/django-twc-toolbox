from __future__ import annotations

import sys
from typing import Generic

from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.http import HttpRequest

from ._typing import ChildModelT
from ._typing import ListOrTuple
from ._typing import ParentModelT

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override  # pyright: ignore[reportUnreachable]


class ReadOnlyModelAdmin(
    Generic[ChildModelT, ParentModelT], BaseModelAdmin[ChildModelT]
):
    can_delete = False
    extra = 0

    @override
    def get_readonly_fields(
        self, request: HttpRequest, obj: ChildModelT | None = None
    ) -> ListOrTuple[str]:
        return [f.name for f in self.model._meta.fields]

    @override
    def has_add_permission(  # type: ignore[override]
        self, request: HttpRequest, obj: ParentModelT | None
    ) -> bool:
        return False

    @override
    def has_change_permission(  # type: ignore[override]
        self, request: HttpRequest, obj: ParentModelT | None = None
    ) -> bool:
        return False


class ReadOnlyStackedInline(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ReadOnlyModelAdmin[ChildModelT, ParentModelT],
    admin.StackedInline[ChildModelT, ParentModelT],
): ...


class ReadOnlyTabularInline(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ReadOnlyModelAdmin[ChildModelT, ParentModelT],
    admin.TabularInline[ChildModelT, ParentModelT],
): ...
