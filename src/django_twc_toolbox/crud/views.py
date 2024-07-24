# pyright: reportUnnecessaryTypeIgnoreComment=false
from __future__ import annotations

import sys
from collections.abc import Callable
from typing import ClassVar
from typing import Literal

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

    # django-template-partials doesn't seem to be able to use a passed in context
    # variable to define partials, e.g. with `list_partial = "object-list"`
    # in the template context:
    #
    # ```htmldjango
    # {% load partials %}
    # {% partialdef list_partial %}
    #   <h1>Hello World!</h1>
    # {% endpartialdef %}
    # ```
    #
    # This does not work, at least the different ways I've tried.
    #
    # However! I am including this class variable in the event I (or someone else)
    # cracks the case and figures out how to get the templatetag to be able to take
    # an outside variable.
    #
    # So the partial name within the `object_list.html` template MUST BE `object-list`,
    # at least for the time being.
    list_partial: ClassVar[Literal["object-list"]] = "object-list"

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
            # This is the only part that is changed from the `neapolitan.views.CRUDView` parent class.
            #
            # If `table_class` is set, that means the view class has `SingleTableMixin` in it's inheritance
            # chain[^1]. `neapolitan.views.CRUDView.get_paginate_by` does not take an argument, whereas
            # `django_tables2.views.SingleTableMixin.get_paginate_by` expects one (`table_data`), so we need
            # to pass in an argument so the view doesn't crash.
            #
            # Now, mind you, `SingleTableMixin.get_paginate_by` doesn't actually **do** anything with that
            # argument, so it's a bit useless. But 🤷 whatareyagonnado?
            #
            # I have opened an issue on neapolitan to add the ability for `CRUDView.get_paginate_by` to take
            # arbitrary args and kwargs by adding `*args, **kwargs`. I may also open an issue on django-tables2
            # to add `None` to the `table_data` argument in `SingleTableMixin.get_paginate_by` since it's unused
            # and presumably only put there to allow people to override and customize?
            #
            # [^1]: Inheritance chain? Is that the correct terminology? Probably not, but you get the idea.

            paginate_by = self.get_paginate_by(queryset)  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue,reportUnknownVariableType]
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

    @override
    def get_template_names(self):
        template_names = super().get_template_names()
        # only render the template partial if:
        # - it's the list view
        # - it's an HTMX request
        # - it's not a paginated request
        #
        # Right now, our custom templates do not have support for rendering template partials when
        # dealing with paginated lists. We could probably update it to add an `hx-target` to the
        # pagination links, but for now we'll just render the entire template.
        if (
            self.role == Role.LIST
            and getattr(self.request, "htmx", False)
            and self.request.htmx
            and not self.kwargs.get(self.page_kwarg, None)  # pyright: ignore[reportAny]
            and not self.request.GET.get(self.page_kwarg, None)
        ):
            template_names = [
                f"{template_name}#{self.list_partial}"
                for template_name in template_names
            ]
        return template_names

    @classmethod
    @override
    def as_view(  # type: ignore[override]
        cls, role: Role, **initkwargs: object
    ) -> Callable[..., HttpResponse]:
        # Check if the list view is being called OR the list view is being called and there is no
        # `table_class` attribute set. If not, we can just return the parent
        # `neapolitan.views.CRUDView.as_view` method to render as normal.

        if role != Role.LIST or cls.table_class is None:
            return super().as_view(role=role, **initkwargs)

        # View is a list view and has the `table_class` attribute set, so we need to override the class
        # returned by adding `django_tables2.views.SingleTableMixin` so that the table can be rendered.
        # I would normally just add this to the base CRUDView up top, but since this class is used for
        # multiple request types, we just scope it to the GET on the list url. Is this overkill? Would this
        # be a bit clearer if it was just set above in the class declaration instead of doing this dance?
        # Unsure. Open to changing this later on in case this is too complicated.
        #
        # We don't need to change anything else about the class (there's already some small logic around
        # dealing with pagination in the `list` method above), so we can get away with just adding the mixin,
        # inheriting from `cls` a.k.a. `django_twc_toolbox.crud.views.CRUDView`, and leaving the body of the
        # new view        # class empty (`...`).
        #
        # Also need to pass in the class variable `table_class` to the `as_view` class method so it's available
        # on the instance.

        class ListViewWithTable(SingleTableMixin, cls): ...  # type: ignore[misc,valid-type]

        return ListViewWithTable.as_view(
            role=role, table_class=cls.table_class, **initkwargs
        )
