# pylint: disable=missing-docstring
from pathlib import Path

import pytest

from fava.core import FavaAPIException
from fava.core import FavaLedger


def test_apiexception():
    with pytest.raises(FavaAPIException) as exception:
        raise FavaAPIException("error")
    exception = exception.value
    assert str(exception) == "error"
    assert str(exception) == exception.message


def test_attributes(example_ledger: FavaLedger) -> None:
    assert len(example_ledger.attributes.accounts) == 61
    assert "Assets" not in example_ledger.attributes.accounts


def test_paths_to_watch(example_ledger: FavaLedger, monkeypatch) -> None:
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [],
    )
    monkeypatch.setitem(example_ledger.options, "documents", ["folder"])
    base = Path(example_ledger.beancount_file_path).parent / "folder"
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [
            str(base / account)
            for account in [
                "Assets",
                "Liabilities",
                "Equity",
                "Income",
                "Expenses",
            ]
        ],
    )


def test_account_metadata(example_ledger: FavaLedger) -> None:
    data = example_ledger.accounts["Assets:US:BofA"].meta
    assert data["address"] == "123 America Street, LargeTown, USA"
    assert data["institution"] == "Bank of America"

    assert not example_ledger.accounts["Assets"].meta
    assert not example_ledger.accounts["NOACCOUNT"].meta


def test_group_entries(example_ledger: FavaLedger, load_doc) -> None:
    """
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2012-12-12 note Expenses:T "test"
    """

    entries, _, __ = load_doc
    assert len(entries) == 3
    data = example_ledger.group_entries_by_type(entries)
    assert data == [("Note", [entries[2]]), ("Transaction", entries[0:2])]


def test_account_uptodate_status(example_ledger: FavaLedger) -> None:
    func = example_ledger.account_uptodate_status
    assert func("Assets:US:BofA") is None
    assert func("Assets:US:BofA:Checking") == "yellow"
    assert func("Liabilities:US:Chase:Slate") == "green"


def test_commodities(example_ledger: FavaLedger) -> None:
    assert len(example_ledger.commodities) == 10
    usd = example_ledger.commodities["USD"]
    assert usd.meta["export"] == "CASH"
