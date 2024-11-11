"""Entries grouped by type."""

from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple
from typing import TYPE_CHECKING

from fava.beans import abc
from fava.beans.account import get_entry_accounts

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Mapping
    from collections.abc import Sequence


class EntriesByType(NamedTuple):
    """Entries grouped by type."""

    Balance: Sequence[abc.Balance]
    Close: Sequence[abc.Close]
    Commodity: Sequence[abc.Commodity]
    Custom: Sequence[abc.Custom]
    Document: Sequence[abc.Document]
    Event: Sequence[abc.Event]
    Note: Sequence[abc.Note]
    Open: Sequence[abc.Open]
    Pad: Sequence[abc.Pad]
    Price: Sequence[abc.Price]
    Query: Sequence[abc.Query]
    Transaction: Sequence[abc.Transaction]


def group_entries_by_type(entries: Sequence[abc.Directive]) -> EntriesByType:
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
    entries: Sequence[abc.Directive],
) -> Mapping[str, Sequence[abc.Directive | TransactionPosting]]:
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
