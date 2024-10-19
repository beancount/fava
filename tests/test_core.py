from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.beans.funcs import hash_entry
from fava.core import EntryNotFoundForHashError
from fava.core import FilteredLedger
from fava.helpers import FavaAPIError
from fava.util.date import Interval
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.core import FavaLedger


def test_apiexception() -> None:
    with pytest.raises(FavaAPIError) as exception:
        raise FavaAPIError("error")  # noqa: EM101
    assert str(exception.value) == "error"


def test_attributes(example_ledger: FavaLedger) -> None:
    assert len(example_ledger.attributes.accounts) == 61
    assert "Assets" not in example_ledger.attributes.accounts


def test_filtered_ledger(
    small_example_ledger: FavaLedger,
) -> None:
    filtered = FilteredLedger(small_example_ledger, account="NONE")
    assert filtered.prices("EUR", "USD")
    assert filtered.prices("UNKNOWN1", "UNKNOWN2") == []
    assert filtered.date_range is None
    assert not filtered.interval_ranges(Interval.MONTH)

    all_entries = FilteredLedger(small_example_ledger)
    closed_acc = "Assets:Account1"
    unclosed_acc = "Expenses:Food"
    assert all_entries.account_is_closed(closed_acc)
    assert not all_entries.account_is_closed(unclosed_acc)

    year_2012 = FilteredLedger(small_example_ledger, time="2012")
    assert not year_2012.account_is_closed(closed_acc)
    assert not year_2012.account_is_closed(unclosed_acc)


def test_ledger_get_entry(
    small_example_ledger: FavaLedger,
) -> None:
    first = small_example_ledger.all_entries[0]
    assert small_example_ledger.get_entry(hash_entry(first)) == first

    with pytest.raises(EntryNotFoundForHashError):
        small_example_ledger.get_entry("asdfa")


def test_paths_to_watch(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert example_ledger.paths_to_watch() == (
        [Path(example_ledger.beancount_file_path)],
        [],
    )
    monkeypatch.setitem(example_ledger.options, "documents", ["folder"])
    base = Path(example_ledger.beancount_file_path).parent / "folder"
    assert example_ledger.paths_to_watch() == (
        [Path(example_ledger.beancount_file_path)],
        [
            base / account
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


def test_group_entries(
    example_ledger: FavaLedger,
    load_doc_entries: list[Directive],
) -> None:
    """
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2010-11-12 * "test"
        Assets:T   4.00 USD
        Expenses:T
    2012-12-12 note Expenses:T "test"
    """

    assert len(load_doc_entries) == 3
    data = example_ledger.group_entries_by_type(load_doc_entries)
    assert data.Note == [load_doc_entries[2]]
    assert data.Transaction == load_doc_entries[0:2]


def test_account_uptodate_status(example_ledger: FavaLedger) -> None:
    accounts = example_ledger.accounts
    assert accounts["Assets:US:BofA"].uptodate_status is None
    assert accounts["Assets:US:BofA:Checking"].uptodate_status == "yellow"
    assert accounts["Liabilities:US:Chase:Slate"].uptodate_status == "green"


def test_account_balance_directive(example_ledger: FavaLedger) -> None:
    today = local_today()
    bal = f"{today} balance Assets:US:BofA:Checking              1632.79 USD\n"

    assert (
        example_ledger.accounts["Assets:US:BofA:Checking"].balance_string
        == bal
    )
    assert example_ledger.accounts.all_balance_directives() == bal


def test_commodity_names(example_ledger: FavaLedger) -> None:
    assert example_ledger.commodities.name("USD") == "US Dollar"
    assert example_ledger.commodities.name("NOCOMMODITY") == "NOCOMMODITY"
    assert example_ledger.commodities.name("VMMXX") == "VMMXX"
