from __future__ import annotations

import sys
from typing import TypeVar

from django.db.models.base import Model

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


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
