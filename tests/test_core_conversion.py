"""Currency conversions."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from fava.beans.abc import Price
from fava.beans.prices import FavaPriceMap
from fava.core.conversion import _CurrencyConversion
from fava.core.conversion import Conversion
from fava.core.conversion import conversion_from_str
from fava.core.conversion import convert_position
from fava.core.conversion import get_cost
from fava.core.conversion import get_market_value
from fava.core.conversion import get_units
from fava.core.inventory import _Amount
from fava.core.inventory import _Cost
from fava.core.inventory import _Position
from fava.core.inventory import CounterInventory
from fava.core.inventory import SimpleCounterInventory
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def _amt(s: str) -> _Amount:
    num, currency = s.split(" ")
    assert num, currency
    return _Amount(Decimal(num), currency)


def _cost(s: str) -> _Cost:
    num, currency = s.split(" ")
    assert num, currency
    return _Cost(Decimal(num), currency, local_today(), "label")


def _pos(s: str) -> _Position:
    match = re.match(r"(.*?) \{(.*)\}", s)
    return (
        _Position(_amt(match.group(1)), _cost(match.group(2)))
        if match
        else _Position(_amt(s), None)
    )


def _inv(s: str) -> CounterInventory:
    res = CounterInventory()
    for p in s.split(","):
        res.add_position(_pos(p.strip()))
    return res


def _simple_inv(s: str) -> SimpleCounterInventory:
    res = SimpleCounterInventory()
    for p in s.split(","):
        amt = _amt(p.strip())
        res.add(amt.currency, amt.number)
    return res


@pytest.mark.parametrize(
    ("conversion", "currencies"),
    [
        ("at_cost", ()),
        ("at_value", ()),
        ("units", ()),
        ("invalid", ("invalid",)),
        ("USD,EUR", ("USD", "EUR")),
        ("EUR", ("EUR",)),
    ],
)
def test_conversion_from_string(
    conversion: str,
    currencies: tuple[str],
) -> None:
    parsed = conversion_from_str(conversion)
    assert isinstance(parsed, Conversion)
    if currencies:
        assert isinstance(parsed, _CurrencyConversion)
        assert parsed._currencies == currencies


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        ("10 USD", "10 USD"),
        ("10 USD {10 EUR}", "10 USD"),
    ],
)
def test_get_units(position: str, expected: str) -> None:
    assert get_units(_pos(position)) == _amt(expected)


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        ("10 USD", "10 USD"),
        ("10 USD {10 EUR}", "100 EUR"),
    ],
)
def test_get_cost(position: str, expected: str) -> None:
    assert get_cost(_pos(position)) == _amt(expected)


@pytest.mark.parametrize(
    ("position", "conversion_date", "expected"),
    [
        # No market value without cost.
        ("10 STOCK", None, "10 STOCK"),
        ("10 STOCK", date(2022, 2, 2), "10 STOCK"),
        # Market value changes with changing prices.
        ("10 STOCK {5 USD}", date(2022, 2, 1), "50 USD"),
        ("10 STOCK {5 USD}", date(2022, 2, 2), "100 USD"),
        ("10 STOCK {5 USD}", date(2022, 2, 4), "200 USD"),
        ("10 STOCK {5 USD}", None, "200 USD"),
    ],
)
def test_get_market_value(
    load_doc_entries: list[Directive],
    position: str,
    conversion_date: date | None,
    expected: str,
) -> None:
    """
    2022-02-02 price STOCK 10 USD
    2022-02-04 price STOCK 20 USD
    """
    prices = FavaPriceMap(
        (e for e in load_doc_entries if isinstance(e, Price)),
    )
    pos = _pos(position)
    assert get_market_value(pos, prices, conversion_date) == _amt(expected)


@pytest.mark.parametrize(
    ("position", "target_currency", "conversion_date", "expected"),
    [
        ("10 STOCK", "EUR", None, "10 STOCK"),
        # Price changes on dates
        ("10 STOCK", "USD", date(2022, 2, 1), "10 STOCK"),
        ("10 STOCK", "USD", date(2022, 2, 2), "100 USD"),
        ("10 STOCK", "USD", date(2022, 2, 3), "100 USD"),
        ("10 STOCK", "USD", date(2022, 2, 4), "200 USD"),
        ("10 STOCK", "USD", None, "200 USD"),
        # Conversion via cost currency
        ("10 STOCK {5 GBP}", "EUR", None, "3600 EUR"),
        ("10 STOCK {5 GBP}", "UNKNOWN", None, "10 STOCK"),
        ("10 STOCK {5 UNKNOWN}", "UNKNOWN2", None, "10 STOCK"),
        ("10 STOCK {5 UNKNOWN}", "UNKNOWN", None, "10 STOCK"),
    ],
)
def test_convert_position(
    load_doc_entries: list[Directive],
    position: str,
    target_currency: str,
    conversion_date: date | None,
    expected: str,
) -> None:
    """
    2022-02-02 price STOCK 10 USD
    2022-02-04 price STOCK 20 USD
    2022-02-04 price STOCK 30 GBP
    2022-02-04 price GBP 12 EUR
    """

    prices = FavaPriceMap(
        (e for e in load_doc_entries if isinstance(e, Price)),
    )
    pos = _pos(position)
    assert convert_position(
        pos,
        target_currency,
        prices,
        conversion_date,
    ) == _amt(expected)


@pytest.mark.parametrize(
    ("inventory", "conversion", "conversion_date", "expected"),
    [
        ("10 STOCK", "EUR", None, "10 STOCK"),
        ("10 STOCK", "at_value", None, "10 STOCK"),
        ("10 STOCK", "units", None, "10 STOCK"),
        ("10 STOCK {5 GBP}", "at_cost", None, "50 GBP"),
        ("10 STOCK {5 GBP},10 STOCK {2 GBP}", "at_cost", None, "70 GBP"),
        ("10 STOCK {5 GBP}", "at_value", None, "300 GBP"),
        ("5 STOCK, 5 STOCK", "EUR", None, "10 STOCK"),
        # Multiple conversions
        ("10 STOCK", "EUR,UNKNOWN", None, "10 STOCK"),
        ("10 STOCK", "EUR,USD", None, "200 USD"),
        ("10 STOCK", "USD,GBP,EUR", None, "200 USD"),
        ("10 STOCK", "GBP,EUR", None, "3600 EUR"),
        # # Conversion via cost currency
        ("10 STOCK {10 GBP}", "USD,GBP,EUR", None, "200 USD"),
        ("10 STOCK {10 GBP}", "EUR", None, "3600 EUR"),
    ],
)
def test_conversion(
    load_doc_entries: list[Directive],
    inventory: str,
    conversion: str,
    conversion_date: date | None,
    expected: str,
) -> None:
    """
    2022-02-02 price STOCK 10 USD
    2022-02-04 price STOCK 20 USD
    2022-02-04 price STOCK 30 GBP
    2022-02-04 price GBP 12 EUR
    """

    prices = FavaPriceMap(
        (e for e in load_doc_entries if isinstance(e, Price)),
    )
    inv = _inv(inventory)
    conv = conversion_from_str(conversion)
    assert conv.apply(
        inv,
        prices=prices,
        date=conversion_date,
    ) == _simple_inv(expected)
