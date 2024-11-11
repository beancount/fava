"""Fava's budget syntax."""

from __future__ import annotations

import datetime

from fava.beans import create
from fava.beans.helpers import replace
from fava.core.accounts import get_last_entry
from fava.core.accounts import uptodate_status
from fava.core.group_entries import TransactionPosting


def test_get_last_entry() -> None:
    assert get_last_entry([]) is None

    posting = create.posting("Assets", create.amount("10 EUR"))
    txn_unrealized = create.transaction(
        {},
        datetime.date(2024, 1, 1),
        flag="U",
        payee="payee",
        narration="narration",
        tags=frozenset(),
        links=frozenset(),
        postings=[posting],
    )
    txn = create.transaction(
        meta={},
        date=datetime.date(2023, 1, 1),
        flag="*",
        payee="payee",
        narration="narration",
        tags=frozenset(),
        links=frozenset(),
        postings=[posting],
    )
    note = create.note(
        meta={},
        date=datetime.date(2025, 1, 1),
        account="Assets",
        comment="a note",
    )

    entries = [
        TransactionPosting(txn, posting),
        TransactionPosting(txn_unrealized, posting),
    ]

    assert get_last_entry([note]) == note
    assert get_last_entry(entries) == txn
    assert get_last_entry([*entries, note]) == note


def test_uptodate_status() -> None:
    assert uptodate_status([]) is None

    note = create.note(
        meta={},
        date=datetime.date(2025, 1, 1),
        account="Assets",
        comment="a note",
    )
    balance = create.balance(
        meta={},
        date=datetime.date(2024, 1, 1),
        account="Assets",
        amount=create.amount("10 EUR"),
    )
    balance_diff = replace(balance, diff_amount=create.amount("1 EUR"))

    assert uptodate_status([balance, note]) == "green"
    assert uptodate_status([balance_diff, note]) == "red"
