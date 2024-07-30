from __future__ import annotations

from collections.abc import Generator
from collections.abc import Sequence
from typing import cast

from django import template
from django.db import models
from neapolitan.views import Role

from django_twc_toolbox.crud.views import CRUDView

register = template.Library()


def action_links(view: CRUDView, object: models.Model):
    actions = {
        "detail": {
            "url": Role.DETAIL.maybe_reverse(view, object),
            "text": "View",
        },
        "update": {
            "url": Role.UPDATE.maybe_reverse(view, object),
            "text": "Edit",
        },
        "delete": {
            "url": Role.DELETE.maybe_reverse(view, object),
            "text": "Delete",
        },
    }
    return actions


@register.inclusion_tag("neapolitan/partial/detail.html")
def object_detail(object: models.Model, view: CRUDView):
    """
    Renders a detail view of an object with the given fields.

    Inclusion tag usage::

        {% object_detail object view %}

    Template: ``neapolitan/partial/detail.html`` - Will render a table of the
    object's fields.
    """

    fields = view.get_fields()

    def iter() -> Generator[tuple[str, str], None, None]:
        for f in fields:
            mf = object._meta.get_field(f)
            if view.detail_field_renderers:
                renderer = view.detail_field_renderers.get(f, None)

                if renderer is None:
                    continue

                if callable(renderer):
                    rendered = renderer(field=mf, object=object)
                else:
                    msg = f"Field renderer for `{f}` should be a callable that returns a string"
                    raise template.TemplateSyntaxError(msg)
            else:
                rendered = str(getattr(object, f))

            yield (cast(str, mf.verbose_name), rendered)  # type: ignore[union-attr]

    return {"object": iter()}


@register.inclusion_tag("neapolitan/partial/list.html")
def object_list(objects: Sequence[models.Model], view: CRUDView):
    """
    Renders a list of objects with the given fields.

    Inclusion tag usage::

        {% object_list objects view %}

    Template: ``neapolitan/partial/list.html`` — Will render a table of objects
    with links to view, edit, and delete views.
    """

    fields = view.get_fields()
    headers = [cast(str, objects[0]._meta.get_field(f).verbose_name) for f in fields]  # type: ignore[union-attr]
    object_list = [
        {
            "object": object,
            "fields": [{"name": f, "value": str(getattr(object, f))} for f in fields],
            "actions": action_links(view, object),
        }
        for object in objects
    ]

    return {
        "headers": headers,
        "object_list": object_list,
    }
