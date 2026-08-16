from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

import pytest
from beancount.core.account import has_component

from fava.beans import create
from fava.beans.account import get_entry_accounts
from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import FilterError
from fava.core.filters import TimeFilter

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def test_emoji_search_in_narration() -> None:
    txn = create.transaction(
        {},
        datetime.date(2026, 6, 24),
        "*",
        "Cafe ☕",
        "Coffee",
        frozenset(),
        frozenset(),
        [create.posting("Expenses:Food:Coffee", "5.00 AUD")],
    )
    filter_ = AdvancedFilter("☕")
    assert filter_.apply([txn]) == [txn]

    filter_no_match = AdvancedFilter("⛽")
    assert filter_no_match.apply([txn]) == []


@pytest.mark.parametrize(
    ("string", "number"),
    [
        ('any(account:"Assets:US:ETrade")', 48),
        ('all(-account:"Assets:US:ETrade")', 1826 - 48),
        ("#test", 2),
        ("#test,#nomatch", 2),
        ("-#nomatch", 1826),
        ("-#nomatch -#nomatch", 1826),
        ("-#nomatch -#test", 1824),
        ("-#test", 1824),
        ("^test-link", 3),
        ("^test-link,#test", 4),
        ("^test-link -#test", 2),
        ("payee:BayBook", 62),
        ("BayBook", 62),
        ("(payee:BayBook, #test,#nomatch) -#nomatch", 64),
        ('payee:"BayBo.*"', 62),
        ('payee:"baybo.*"', 62),
        (r'number:"\d*"', 3),
        ('not_a_meta_key:".*"', 0),
        ('name:".*ETF"', 4),
        ('name:".*ETF$"', 3),
        ('name:".*etf"', 4),
        ('name:".*etf$"', 3),
        ('any(overage:"GB$")', 1),
        ("=26.87", 1),
        (">=17500", 3),
        (">=17500 <18000", 1),
        ("any(units >= 17500)", 3),
    ],
)
def test_advanced_filter(
    example_ledger: FavaLedger,
    string: str,
    number: int,
) -> None:
    filter_ = AdvancedFilter(string)
    filtered_entries = filter_.apply(example_ledger.all_entries)
    assert len(filtered_entries) == number


def test_null_meta_posting() -> None:
    filter_ = AdvancedFilter('any(some_meta:"1")')

    txn = create.transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "",
        "",
        frozenset(),
        frozenset(),
        [create.posting("Assets:ETrade:Cash", "100 USD")],
    )
    assert txn.postings[0].meta is None
    assert len(filter_.apply([txn])) == 0


def test_account_filter(example_ledger: FavaLedger) -> None:
    account_filter = AccountFilter("")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert filtered_entries is example_ledger.all_entries

    account_filter = AccountFilter("Assets")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 541
    for entry in filtered_entries:
        assert any(
            has_component(a, "Assets") for a in get_entry_accounts(entry)
        )

    account_filter = AccountFilter(".*US:State")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 67


def test_time_filter(example_ledger: FavaLedger) -> None:
    time_filter = TimeFilter(
        example_ledger.options,
        example_ledger.fava_options,
        "2017",
    )

    date_range = time_filter.date_range
    assert date_range
    assert date_range.begin == datetime.date(2017, 1, 1)
    assert date_range.end == datetime.date(2018, 1, 1)
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 83

    time_filter = TimeFilter(
        example_ledger.options,
        example_ledger.fava_options,
        "1000",
    )
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert not filtered_entries

    with pytest.raises(FilterError):
        TimeFilter(
            example_ledger.options,
            example_ledger.fava_options,
            "no_date",
        )


def test_filter_error_contains_the_filter() -> None:
    with pytest.raises(
        FilterError,
        match=re.escape("who:\"fff': Unexpected '\"' in parsed expression."),
    ):
        AdvancedFilter('who:"fff')
