from __future__ import annotations

import sys
from typing import ClassVar

from django.core.exceptions import ImproperlyConfigured
from neapolitan.views import CRUDView as NeapolitanCRUDView
from neapolitan.views import Role

if sys.version_info >= (3, 12):
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override  # pyright: ignore[reportUnreachable]


class CRUDView(NeapolitanCRUDView):
    paginate_by = 100

    detail_fields: ClassVar[list[str] | None] = None
    list_fields: ClassVar[list[str] | None] = None

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["list_view_url"] = Role.LIST.maybe_reverse(self)
        if self.object is not None:
            context["delete_view_url"] = Role.DELETE.maybe_reverse(self, self.object)
            context["detail_view_url"] = Role.DETAIL.maybe_reverse(self, self.object)
            context["update_view_url"] = Role.UPDATE.maybe_reverse(self, self.object)
        return context

    def get_fields(self):
        match self.role:
            case Role.DETAIL:
                fields = self.get_detail_fields()
            case Role.LIST:
                fields = self.get_list_fields()
            case _:
                fields = None

        if fields is not None:
            return fields

        if self.fields is not None:
            return self.fields

        msg = "'%s' must define 'fields' or override 'get_fields()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_detail_fields(self):
        return self.detail_fields

    def get_list_fields(self):
        return self.list_fields
