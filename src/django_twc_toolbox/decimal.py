from __future__ import annotations

from decimal import Decimal
from decimal import InvalidOperation
from typing import TypeVar
from typing import overload

T = TypeVar("T", float, str, Decimal)


@overload
def format_decimal_places(number: float, *, decimal_places: int = 2) -> str: ...
@overload
def format_decimal_places(number: str, *, decimal_places: int = 2) -> str: ...
@overload
def format_decimal_places(number: Decimal, *, decimal_places: int = 2) -> Decimal: ...
def format_decimal_places(number: T, *, decimal_places: int = 2) -> str | Decimal:
    try:
        decimal_value = Decimal(str(number))
    except InvalidOperation as err:
        msg = f"Invalid number input: {number}"
        raise ValueError(msg) from err

    str_value = str(decimal_value)
    parts = str_value.split(".")

    if len(parts) == 1:
        formatted_str = f"{str_value}.{'0' * decimal_places}"
    else:
        integer_part, fractional_part = parts
        fractional_part = fractional_part.rstrip("0")
        if len(fractional_part) < decimal_places:
            fractional_part = fractional_part.ljust(decimal_places, "0")
        formatted_str = f"{integer_part}.{fractional_part}"

    if isinstance(number, (float, str)):
        return formatted_str
    else:
        return Decimal(formatted_str)
