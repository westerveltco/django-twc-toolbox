from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from urllib.parse import quote

from django.http import HttpResponse
from django.urls import reverse as dj_reverse
from django.utils.functional import lazy
from django.utils.http import urlencode


def reverse(
    viewname: Callable[..., HttpResponse] | str | None,
    urlconf: str | None = None,
    args: Sequence[object] | None = None,
    kwargs: dict[str, object] | None = None,
    current_app: str | None = None,
    # https://github.com/typeddjango/django-stubs/blob/c7d734af5703712ad9bb78ff5be902c760ccb637/django-stubs/utils/http.pyi#L13-L17
    query: Mapping[str, str | bytes | int | Iterable[str | bytes | int]]
    | Iterable[tuple[str, str | bytes | int | Iterable[str | bytes | int]]]
    | None = None,
    fragment: str | None = None,
) -> str:
    url = dj_reverse(
        viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app
    )
    if query:
        url += f"?{urlencode(query)}"
    if fragment:
        url += f"#{quote(fragment)}"
    return url


reverse_lazy = lazy(reverse, str)
