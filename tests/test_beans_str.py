from __future__ import annotations

import datetime
from decimal import Decimal
from textwrap import dedent

import pytest
from beancount.core.position import CostSpec

from fava.beans import create
from fava.beans.str import to_string


def test_to_string_invalid() -> None:
    with pytest.raises(TypeError):
        to_string({})  # type: ignore[arg-type]


def test_to_string_amount() -> None:
    amount = create.amount("10 EUR")
    assert amount.number == Decimal(10)
    assert to_string(amount) == "10 EUR"


def test_to_string_cost() -> None:
    one = Decimal(1)
    date = datetime.date(2022, 1, 1)
    cost = create.cost(one, "EUR", date)
    assert to_string(cost) == "1 EUR, 2022-01-01"

    cost = create.cost(one, "EUR", date, label="asdf")
    assert to_string(cost) == '1 EUR, 2022-01-01, "asdf"'


def test_to_string_position() -> None:
    one = Decimal(1)
    date = datetime.date(2022, 1, 1)
    amount = create.amount("10 EUR")
    cost = create.cost(one, "EUR", date)
    position = create.position(amount, cost)
    assert to_string(position) == "10 EUR {1 EUR, 2022-01-01}"


def _spec(
    *,
    number_per: Decimal | None = None,
    number_total: Decimal | None = None,
    currency: str | None = None,
    date: datetime.date | None = None,
    label: str | None = None,
    merge: bool | None = None,
) -> CostSpec:
    return CostSpec(number_per, number_total, currency, date, label, merge)


def test_to_string_cost_spec() -> None:
    one = Decimal(1)
    two = Decimal(2)
    date = datetime.date(2022, 1, 1)
    eur = "EUR"
    assert not to_string(_spec())
    assert to_string(_spec(number_per=one)) == "1"
    assert to_string(_spec(number_total=two)) == "# 2"
    assert to_string(_spec(number_per=one, number_total=two)) == "1 # 2"
    assert to_string(_spec(number_per=one, currency=eur)) == "1 EUR"
    assert to_string(_spec(number_total=two, currency=eur)) == "# 2 EUR"
    assert (
        to_string(_spec(number_per=one, number_total=two, currency=eur))
        == "1 # 2 EUR"
    )
    assert to_string(_spec(number_per=one, date=date)) == "1, 2022-01-01"
    assert to_string(_spec(number_per=one, label="label")) == '1, "label"'
    assert to_string(_spec(number_per=one, merge=True)) == "1, *"
    assert (
        to_string(_spec(number_per=one, date=date, label="label", merge=True))
        == '1, 2022-01-01, "label", *'
    )


def test_to_string_transaction() -> None:
    postings = [
        create.posting("Liabilities:US:Chase:Slate", "-10.00 USD"),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        datetime.date(2016, 1, 1),
        "*",
        "payee",
        "narr",
        postings=postings,
    )
    assert to_string(transaction, 50, 4) == dedent("""\
        2016-01-01 * "payee" "narr"
            Liabilities:US:Chase:Slate            -10.00 USD
            Expenses:Food                          10.00 USD
        """)


def test_to_string_transaction_with_price() -> None:
    postings = [
        create.posting("Liabilities:US:Chase:Slate", "-10.00 USD"),
        create.posting("Expenses:Food", units="10.00 USD", price="10 EUR"),
    ]

    transaction = create.transaction(
        {},
        datetime.date(2016, 1, 1),
        "*",
        "payee",
        "narr",
        postings=postings,
    )
    assert to_string(transaction, 50, 4) == dedent("""\
        2016-01-01 * "payee" "narr"
            Liabilities:US:Chase:Slate            -10.00 USD
            Expenses:Food                          10.00 USD @ 10 EUR
        """)
