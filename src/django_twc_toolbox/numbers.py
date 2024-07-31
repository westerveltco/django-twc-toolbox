from __future__ import annotations

from decimal import Decimal
from decimal import InvalidOperation
from typing import TypeVar
from typing import overload

T = TypeVar("T", float, str, Decimal)


@overload
def format_number_no_round(number: float, *, decimal_places: int = 2) -> str: ...
@overload
def format_number_no_round(number: str, *, decimal_places: int = 2) -> str: ...
@overload
def format_number_no_round(number: Decimal, *, decimal_places: int = 2) -> Decimal: ...
def format_number_no_round(number: T, *, decimal_places: int = 2) -> str | Decimal:
    """Formats a number with the number of decimal places specified without rounding.

    It takes a number and ensures it has at least the number of decimal places passed
    it as an argument, defaulting to 2. This csn be useful for displaying and working
    with currency as it does not round the number, preserving any additional precision
    beyond the decimal places if present.

    Args:
        number (T): The number to format. Can be a float, str, or Decimal.
        decimal_places (int, optional): Minimum number of decimal places to display.
            Defaults to 2.

    Returns:
        str | Decimal: The formatted number as a string if the input was a float or str,
            or as a Decimal if the input was a Decimal.

    Raises:
        ValueError: If the input cannot be converted to a valid number.

    Examples:
        >>> format_number_no_round(123.4)
        '123.40'
        >>> format_number_no_round(123.45)
        '123.45'
        >>> format_number_no_round(123.456)
        '123.456'
        >>> format_number_no_round(123.4560)
        '123.456'
        >>> format_number_no_round(123.45600)
        '123.456'
        >>> format_number_no_round(123.45600, decimal_places=5)
        '123.45600'
        >>> format_number_no_round(Decimal('123.4'))
        Decimal('123.40')
    """
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

    if isinstance(number, (float | str)):
        return formatted_str
    else:
        return Decimal(formatted_str)
