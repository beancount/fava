"""Entries grouped by type."""

from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple

from fava.beans import abc
from fava.beans.account import get_entry_accounts


class EntriesByType(NamedTuple):
    """Entries grouped by type."""

    Balance: list[abc.Balance]
    Close: list[abc.Close]
    Commodity: list[abc.Commodity]
    Custom: list[abc.Custom]
    Document: list[abc.Document]
    Event: list[abc.Event]
    Note: list[abc.Note]
    Open: list[abc.Open]
    Pad: list[abc.Pad]
    Price: list[abc.Price]
    Query: list[abc.Query]
    Transaction: list[abc.Transaction]


def group_entries_by_type(entries: list[abc.Directive]) -> EntriesByType:
    """Group entries by type.

    Arguments:
        entries: A list of entries to group.

    Returns:
        A namedtuple containing the grouped lists of entries.
    """
    entries_by_type = EntriesByType(
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for entry in entries:
        getattr(entries_by_type, entry.__class__.__name__).append(entry)
    return entries_by_type


class TransactionPosting(NamedTuple):
    """Pair of a transaction and a posting."""

    transaction: abc.Transaction
    posting: abc.Posting


def group_entries_by_account(
    entries: list[abc.Directive],
) -> dict[str, list[abc.Directive | TransactionPosting]]:
    """Group entries by account.

    Arguments:
        entries: A list of entries.

    Returns:
        A dict mapping account names to their entries.
    """
    res: dict[str, list[abc.Directive | TransactionPosting]] = defaultdict(
        list,
    )

    for entry in entries:
        if isinstance(entry, abc.Transaction):
            for posting in entry.postings:
                res[posting.account].append(TransactionPosting(entry, posting))
        else:
            for account in get_entry_accounts(entry):
                res[account].append(entry)

    return dict(sorted(res.items()))
