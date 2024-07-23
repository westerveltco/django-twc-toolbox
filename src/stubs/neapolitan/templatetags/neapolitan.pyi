from collections.abc import Iterable

from django.db import models
from django.utils.safestring import SafeString
from neapolitan.views import CRUDView

def action_links(view: CRUDView, object: models.Model) -> SafeString: ...
def object_detail(
    object: models.Model, fields: list[str]
) -> dict[str, tuple[str, str]]: ...
def object_list(
    objects: Iterable[models.Model], view: CRUDView
) -> dict[str, list[str | dict[str, models.Model | list[str] | SafeString]]]: ...
