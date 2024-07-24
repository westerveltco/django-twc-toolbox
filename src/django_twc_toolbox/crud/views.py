# pyright: reportUnnecessaryTypeIgnoreComment=false
from __future__ import annotations

import sys
from collections.abc import Callable
from typing import ClassVar

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django_tables2 import tables
from django_tables2.views import SingleTableMixin
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

    table_class: ClassVar[type[tables.Table] | None] = None
    table_data: ClassVar[dict[str, object] | None] = None

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

    @override
    def list(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> TemplateResponse:
        """GET handler for the list view."""

        queryset = self.get_queryset()
        filterset = self.get_filterset(queryset)
        if filterset is not None:
            queryset = filterset.qs

        if not self.allow_empty and not queryset.exists():
            raise Http404

        if self.table_class is not None:
            paginate_by = self.get_paginate_by(queryset)  # type: ignore[call-arg,reportCallIssue,reportUnknownVariableType]
        else:
            paginate_by = self.get_paginate_by()

        if paginate_by is None:
            # Unpaginated response
            self.object_list = queryset
            context = self.get_context_data(
                page_obj=None,
                is_paginated=False,
                paginator=None,
                filterset=filterset,
            )
        else:
            # Paginated response
            page = self.paginate_queryset(queryset, paginate_by)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
                filterset=filterset,
            )

        return self.render_to_response(context)

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["list_view_url"] = Role.LIST.maybe_reverse(self)
        if self.object is not None:
            context["delete_view_url"] = Role.DELETE.maybe_reverse(self, self.object)
            context["detail_view_url"] = Role.DETAIL.maybe_reverse(self, self.object)
            context["update_view_url"] = Role.UPDATE.maybe_reverse(self, self.object)
        return context

    @classmethod
    @override
    def as_view(  # type: ignore[override]
        cls, role: Role, **initkwargs: object
    ) -> Callable[..., HttpResponse]:
        if role != Role.LIST or cls.table_class is None:
            return super().as_view(role=role, **initkwargs)

        class ListViewWithTable(SingleTableMixin, cls): ...  # type: ignore[misc,valid-type]

        return ListViewWithTable.as_view(
            role=role, table_class=cls.table_class, **initkwargs
        )
