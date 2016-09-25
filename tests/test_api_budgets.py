from datetime import date

from beancount.core.number import Decimal
from beancount.parser import parser
import pytest

from fava.api.budgets import (_parse_budget_entry, parse_budgets,
                              calculate_budget)


@pytest.fixture
def budgets_doc(load_doc):
    entries, _, _ = load_doc
    budgets, _ = parse_budgets(entries)
    return budgets


def _get_budgets(beancount_string):
    entries, _, _ = parser.parse_string(beancount_string, dedent=True)
    budgets, _ = parse_budgets(entries)
    return budgets


def test_budgets(budgets_doc):
    """
    2016-01-01 custom "budget" Expenses:Groceries "weekly" 100.00 CNY
    2016-06-01 custom "budget" Expenses:Groceries "weekly"  10.00 EUR"""
    budgets = calculate_budget(budgets_doc, 'Expenses:Groceries',
                               date(2016, 6, 1), date(2016, 6, 8))
    assert budgets['CNY'] == Decimal(100)
    assert budgets['EUR'] == Decimal(10)


def test__parse_budget_entry(load_doc):
    """
    2016-05-01 custom "budget"
    2016-05-01 custom "budget" "daily" 2.5 EUR
    2016-05-01 custom "budget" Expenses:Books "daily" 2.5 EUR"""
    entries, _, _ = load_doc
    with pytest.raises(TypeError):
        _parse_budget_entry(entries[0])
    with pytest.raises(IndexError):
        _parse_budget_entry(entries[1])
    _parse_budget_entry(entries[2])


def test_budgets_daily(budgets_doc):
    """
    2016-05-01 custom "budget" Expenses:Books "daily" 2.5 EUR"""
    BUDGET = Decimal(2.5)

    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 5, 1),
                            date(2016, 5, 2))['EUR'] == BUDGET
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 5, 1),
                            date(2016, 5, 3))['EUR'] == BUDGET * 2
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 9, 2),
                            date(2016, 9, 3))['EUR'] == BUDGET
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2018, 12, 31),
                            date(2019, 1, 1))['EUR'] == BUDGET


def test_budgets_weekly(budgets_doc):
    """
    2016-05-01 custom "budget" Expenses:Books "weekly" 21 EUR"""
    BUDGET = Decimal(21)

    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 5, 1),
                            date(2016, 5, 2))['EUR'] == BUDGET / 7
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 9, 1),
                            date(2016, 9, 2))['EUR'] == BUDGET / 7


def test_budgets_monthly(budgets_doc):
    """
    2014-05-01 custom "budget" Expenses:Books "monthly" 100 EUR"""
    BUDGET = Decimal(100)

    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 1, 1),
                            date(2016, 1, 2))['EUR'] == BUDGET / 31
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 2, 1),
                            date(2016, 2, 2))['EUR'] == BUDGET / 29
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2018, 3, 31),
                            date(2018, 4, 1))['EUR'] == BUDGET / 31


def test_budgets_doc_quarterly(budgets_doc):
    """
    2014-05-01 custom "budget" Expenses:Books "quarterly" 123456.7 EUR"""
    BUDGET = Decimal("123456.7")

    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 2, 1),
                            date(2016, 2, 2))['EUR'] == BUDGET / 91
    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2016, 8, 15),
                            date(2016, 8, 16))['EUR'] == BUDGET / 92


def test_budgets_doc_yearly(budgets_doc):
    """
    2010-01-01 custom "budget" Expenses:Books "yearly" 99999.87 EUR"""
    BUDGET = Decimal("99999.87")

    assert calculate_budget(budgets_doc, 'Expenses:Books', date(2011, 2, 1),
                            date(2011, 2, 2))['EUR'] == BUDGET / 365
