from __future__ import annotations

import sys
from typing import TypeAlias
from typing import TypeVar

from django.db.models.base import Model

_K = TypeVar("_K")

ListOrTuple: TypeAlias = list[_K] | tuple[_K, ...] | tuple[()]

ChildModelT = TypeVar("ChildModelT", bound=Model)
ParentModelT = TypeVar("ParentModelT", bound=Model)


if sys.version_info >= (3, 12):
    from typing import override as typing_override
else:  # pragma: no cover
    from typing_extensions import (
        override as typing_override,  # pyright: ignore[reportUnreachable]
    )

override = typing_override
