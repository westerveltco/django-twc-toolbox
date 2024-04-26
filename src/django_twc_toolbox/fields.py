from __future__ import annotations

from functools import partial

from charidfield import CharIDField
from cuid import cuid

CuidField = partial(
    CharIDField,
    default=cuid,
    max_length=30,
    help_text="cuid-format identifier for this entity.",
)
