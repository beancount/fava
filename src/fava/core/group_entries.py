"""Entries grouped by type."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import TYPE_CHECKING

from fava.beans import abc
from fava.beans.account import get_entry_accounts

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Mapping
    from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class EntriesByType:
    """Entries grouped by type."""

    Balance: Sequence[abc.Balance] = field(default_factory=list)
    Close: Sequence[abc.Close] = field(default_factory=list)
    Commodity: Sequence[abc.Commodity] = field(default_factory=list)
    Custom: Sequence[abc.Custom] = field(default_factory=list)
    Document: Sequence[abc.Document] = field(default_factory=list)
    Event: Sequence[abc.Event] = field(default_factory=list)
    Note: Sequence[abc.Note] = field(default_factory=list)
    Open: Sequence[abc.Open] = field(default_factory=list)
    Pad: Sequence[abc.Pad] = field(default_factory=list)
    Price: Sequence[abc.Price] = field(default_factory=list)
    Query: Sequence[abc.Query] = field(default_factory=list)
    Transaction: Sequence[abc.Transaction] = field(default_factory=list)

    def count_by_type(self) -> dict[str, int]:
        """Summarised counts by type."""
        return {f.name: len(getattr(self, f.name)) for f in fields(self)}


def group_entries_by_type(entries: Sequence[abc.Directive]) -> EntriesByType:
    """Group entries by type.

    Arguments:
        entries: A list of entries to group.

    Returns:
        The grouped lists of entries.
    """
    entries_by_type = EntriesByType()
    for entry in entries:
        getattr(entries_by_type, entry.__class__.__name__).append(entry)
    return entries_by_type


@dataclass(frozen=True, slots=True)
class TransactionPosting:
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
