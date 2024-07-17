from __future__ import annotations

import sys
from typing import TypeVar

from django.db.models.base import Model

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias  # pyright: ignore[reportUnreachable]


_K = TypeVar("_K")

if sys.version_info >= (3, 10):
    ListOrTuple: TypeAlias = list[_K] | tuple[_K, ...] | tuple[()]
else:
    from typing import List
    from typing import Tuple
    from typing import Union

    ListOrTuple: TypeAlias = Union[List[_K], Tuple[_K, ...], Tuple[()]]

ChildModelT = TypeVar("ChildModelT", bound=Model)
ParentModelT = TypeVar("ParentModelT", bound=Model)


if sys.version_info >= (3, 12):
    from typing import override as typing_override
else:  # pragma: no cover
    from typing_extensions import (
        override as typing_override,  # pyright: ignore[reportUnreachable]
    )

override = typing_override
