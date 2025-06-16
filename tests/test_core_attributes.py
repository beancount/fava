from __future__ import annotations

from typing import TYPE_CHECKING

from fava.core.attributes import get_active_years
from fava.util.date import FiscalYearEnd

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.core import FavaLedger


def test_get_active_years(load_doc_entries: list[Directive]) -> None:
    """
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2011-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2011-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2012-12-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    """
    assert get_active_years(load_doc_entries, FiscalYearEnd(12, 31)) == [
        "2012",
        "2011",
        "2010",
    ]
    assert get_active_years(load_doc_entries, FiscalYearEnd(12, 1)) == [
        "FY2013",
        "FY2011",
        "FY2010",
    ]
    assert get_active_years(load_doc_entries, FiscalYearEnd(11, 1)) == [
        "FY2013",
        "FY2012",
        "FY2011",
    ]
    assert get_active_years(load_doc_entries, FiscalYearEnd(15, 31)) == [
        "FY2012",
        "FY2011",
        "FY2010",
    ]


def test_payee_accounts(example_ledger: FavaLedger) -> None:
    attr = example_ledger.attributes
    assert attr.payee_accounts("NOTAPAYEE") == attr.accounts

    verizon = attr.payee_accounts("Verizon Wireless")
    assert verizon[:2] == ["Assets:US:BofA:Checking", "Expenses:Home:Phone"]
    assert len(verizon) == len(attr.accounts)


def test_payee_transaction(example_ledger: FavaLedger) -> None:
    attr = example_ledger.attributes
    assert attr.payee_transaction("NOTAPAYEE") is None

    txn = attr.payee_transaction("BayBook")
    assert txn
    assert str(txn.date) == "2016-05-05"


def test_narration_transaction(example_ledger: FavaLedger) -> None:
    attr = example_ledger.attributes
    assert attr.narration_transaction("NOTANARRATION") is None

    txn = attr.narration_transaction("Monthly bank fee")
    assert txn
    assert str(txn.date) == "2016-05-04"


def test_narrations(example_ledger: FavaLedger) -> None:
    attr = example_ledger.attributes
    expected_narrations = [
        "Investing 40% of cash in VBMPX",
        "Investing 60% of cash in RGAGX",
        "Payroll",
        "Buying groceries",
        "Eating out alone",
        "Employer match for contribution",
        "Eating out with Julie",
        "Eating out ",
        "Eating out after work",
        "Eating out with Bill",
        "Eating out with Natasha",
        "Monthly bank fee",
        "Paying off credit card",
        "Eating out with Joe",
        "Paying the rent",
        "Tram tickets",
        "Eating out with work buddies",
        "Buy shares of VEA",
        "Buy shares of GLD",
        "Dividends on portfolio",
        "Transfering accumulated savings to other account",
        "Buy shares of ITOT",
        "Buy shares of VHT",
        "Consume vacation days",
        "Sell shares of GLD",
        "STATE TAX & FINANC PYMT",
        "FEDERAL TAXPYMT",
        "Allowed contributions for one year",
        "Sell shares of VEA",
        "Filing taxes for 2015",
        "Sell shares of VHT",
        "Sell shares of ITOT",
        "Filing taxes for 2014",
        "Opening Balance for checking account",
        "Árvíztűrő tükörfúrógép",
    ]
    assert attr.narrations() == expected_narrations
