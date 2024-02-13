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
