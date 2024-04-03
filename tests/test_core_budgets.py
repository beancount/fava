"""Fava's budget syntax."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from fava.core.budgets import calculate_budget
from fava.core.budgets import calculate_budget_children
from fava.core.budgets import parse_budgets

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Custom
    from fava.core.budgets import BudgetDict


def test_budgets(load_doc_custom_entries: list[Custom]) -> None:
    """
    2016-01-01 custom "budget" Expenses:Groceries "weekly" 100.00 CNY
    2016-06-01 custom "budget" Expenses:Groceries "weekly"  10.00 EUR
    2016-06-01 custom "budget" Expenses:Groceries "asdfasdf"  10.00 EUR
    2016-06-01 custom "budget" Expenses:Groceries 10.00 EUR
    """
    budgets, errors = parse_budgets(load_doc_custom_entries)

    assert len(errors) == 2

    empty = calculate_budget(
        budgets,
        "Expenses",
        date(2016, 6, 1),
        date(2016, 6, 8),
    )
    assert not empty

    budgets_ = calculate_budget(
        budgets,
        "Expenses:Groceries",
        date(2016, 6, 1),
        date(2016, 6, 8),
    )

    assert budgets_["CNY"] == Decimal(100)
    assert budgets_["EUR"] == Decimal(10)


def test_budgets_daily(budgets_doc: BudgetDict) -> None:
    """
    2016-05-01 custom "budget" Expenses:Books "daily" 2.5 EUR"""

    assert "EUR" not in calculate_budget(
        budgets_doc,
        "Expenses:Books",
        date(2010, 2, 1),
        date(2010, 2, 2),
    )

    for start, end, num in [
        (date(2016, 5, 1), date(2016, 5, 2), Decimal("2.5")),
        (date(2016, 5, 1), date(2016, 5, 3), Decimal("5.0")),
        (date(2016, 9, 2), date(2016, 9, 3), Decimal("2.5")),
        (date(2018, 12, 31), date(2019, 1, 1), Decimal("2.5")),
    ]:
        budget = calculate_budget(budgets_doc, "Expenses:Books", start, end)
        assert budget["EUR"] == num


def test_budgets_weekly(budgets_doc: BudgetDict) -> None:
    """
    2016-05-01 custom "budget" Expenses:Books "weekly" 21 EUR"""

    for start, end, num in [
        (date(2016, 5, 1), date(2016, 5, 2), Decimal(21) / 7),
        (date(2016, 9, 1), date(2016, 9, 2), Decimal(21) / 7),
    ]:
        budget = calculate_budget(budgets_doc, "Expenses:Books", start, end)
        assert budget["EUR"] == num


def test_budgets_monthly(budgets_doc: BudgetDict) -> None:
    """
    2014-05-01 custom "budget" Expenses:Books "monthly" 100 EUR"""

    for start, end, num in [
        (date(2016, 5, 1), date(2016, 5, 2), Decimal(100) / 31),
        (date(2016, 2, 1), date(2016, 2, 2), Decimal(100) / 29),
        (date(2018, 3, 31), date(2018, 4, 1), Decimal(100) / 31),
    ]:
        budget = calculate_budget(budgets_doc, "Expenses:Books", start, end)
        assert budget["EUR"] == num


def test_budgets_doc_quarterly(budgets_doc: BudgetDict) -> None:
    """
    2014-05-01 custom "budget" Expenses:Books "quarterly" 123456.7 EUR"""

    for start, end, num in [
        (date(2016, 5, 1), date(2016, 5, 2), Decimal("123456.7") / 91),
        (date(2016, 8, 15), date(2016, 8, 16), Decimal("123456.7") / 92),
    ]:
        budget = calculate_budget(budgets_doc, "Expenses:Books", start, end)
        assert budget["EUR"] == num


def test_budgets_doc_yearly(budgets_doc: BudgetDict) -> None:
    """
    2010-01-01 custom "budget" Expenses:Books "yearly" 99999.87 EUR"""

    budget = calculate_budget(
        budgets_doc,
        "Expenses:Books",
        date(2011, 2, 1),
        date(2011, 2, 2),
    )
    assert budget["EUR"] == Decimal("99999.87") / 365


def test_budgets_children(budgets_doc: BudgetDict) -> None:
    """
    2017-01-01 custom "budget" Expenses:Books "daily" 10.00 USD
    2017-01-01 custom "budget" Expenses:Books:Notebooks "daily" 2.00 USD"""

    budget = calculate_budget_children(
        budgets_doc,
        "Expenses",
        date(2017, 1, 1),
        date(2017, 1, 2),
    )
    assert budget["USD"] == Decimal("12.00")

    budget = calculate_budget_children(
        budgets_doc,
        "Expenses:Books",
        date(2017, 1, 1),
        date(2017, 1, 2),
    )
    assert budget["USD"] == Decimal("12.00")

    budget = calculate_budget_children(
        budgets_doc,
        "Expenses:Books:Notebooks",
        date(2017, 1, 1),
        date(2017, 1, 2),
    )
    assert budget["USD"] == Decimal("2.00")
