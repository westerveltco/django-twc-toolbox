from __future__ import annotations

from decimal import Decimal

import pytest

from django_twc_toolbox.numbers import format_number_no_round


@pytest.mark.parametrize(
    "number,decimal_places,expected",
    [
        (123.0, 2, "123.00"),
        (123.4, 2, "123.40"),
        (123.4567, 2, "123.4567"),
        (123.4500, 2, "123.45"),
        (0.0, 2, "0.00"),
        (0.1, 2, "0.10"),
        (0.01, 2, "0.01"),
        (0.001, 2, "0.001"),
        (1000000.0, 2, "1000000.00"),
        (1000000.10, 2, "1000000.10"),
        (-123.45, 2, "-123.45"),
        (-123.4500, 2, "-123.45"),
        (-123.4567, 2, "-123.4567"),
        (123.0, 3, "123.000"),
        (123.4, 3, "123.400"),
        (123.456789, 4, "123.456789"),
    ],
)
def test_format_number_no_round_float(number, decimal_places, expected):
    result = format_number_no_round(number, decimal_places=decimal_places)

    assert isinstance(result, str)
    assert result == expected
    assert float(result) == pytest.approx(number)


@pytest.mark.parametrize(
    "number,decimal_places,expected",
    [
        ("123", 2, "123.00"),
        ("123.4", 2, "123.40"),
        ("123.40", 2, "123.40"),
        ("123.4567", 2, "123.4567"),
        ("123.4500", 2, "123.45"),
        ("0", 2, "0.00"),
        ("0.1", 2, "0.10"),
        ("0.01", 2, "0.01"),
        ("0.001", 2, "0.001"),
        ("1000000", 2, "1000000.00"),
        ("1000000.10", 2, "1000000.10"),
        ("-123.45", 2, "-123.45"),
        ("-123.4500", 2, "-123.45"),
        ("-123.4567", 2, "-123.4567"),
        ("123", 3, "123.000"),
        ("123.4", 3, "123.400"),
        ("123.456789", 4, "123.456789"),
    ],
)
def test_format_number_no_round_str(number, decimal_places, expected):
    result = format_number_no_round(number, decimal_places=decimal_places)

    assert isinstance(result, str)
    assert result == expected


@pytest.mark.parametrize(
    "number,decimal_places,expected",
    [
        (Decimal("123"), 2, Decimal("123.00")),
        (Decimal("123.4"), 2, Decimal("123.40")),
        (Decimal("123.40"), 2, Decimal("123.40")),
        (Decimal("123.4567"), 2, Decimal("123.4567")),
        (Decimal("123.4500"), 2, Decimal("123.45")),
        (Decimal("0"), 2, Decimal("0.00")),
        (Decimal("0.1"), 2, Decimal("0.10")),
        (Decimal("0.01"), 2, Decimal("0.01")),
        (Decimal("0.001"), 2, Decimal("0.001")),
        (Decimal("1000000"), 2, Decimal("1000000.00")),
        (Decimal("1000000.10"), 2, Decimal("1000000.10")),
        (Decimal("-123.45"), 2, Decimal("-123.45")),
        (Decimal("-123.4500"), 2, Decimal("-123.45")),
        (Decimal("-123.4567"), 2, Decimal("-123.4567")),
        (Decimal("123"), 3, Decimal("123.000")),
        (Decimal("123.4"), 3, Decimal("123.400")),
        (Decimal("123.456789"), 4, Decimal("123.456789")),
    ],
)
def test_format_number_no_round_decimal(number, decimal_places, expected):
    result = format_number_no_round(number, decimal_places=decimal_places)

    assert isinstance(result, Decimal)
    assert result == expected


@pytest.mark.parametrize(
    "decimal_places, expected",
    [
        (0, "123.456789"),
        (2, "123.456789"),
        (7, "123.4567890"),
    ],
)
def test_format_number_no_round_arg(decimal_places, expected):
    number = "123.456789"

    result = format_number_no_round(number, decimal_places=decimal_places)

    assert result == expected


def test_format_number_no_round_invalid_input():
    with pytest.raises(ValueError):
        format_number_no_round("invalid", decimal_places=2)
