"""Entries grouped by type."""
from __future__ import annotations

from typing import NamedTuple

from beancount.core import data
from beancount.core.data import Entries


class EntriesByType(NamedTuple):
    """Entries grouped by type."""

    Balance: list[data.Balance]
    Close: list[data.Close]
    Commodity: list[data.Commodity]
    Custom: list[data.Custom]
    Document: list[data.Document]
    Event: list[data.Event]
    Note: list[data.Note]
    Open: list[data.Open]
    Pad: list[data.Pad]
    Price: list[data.Price]
    Query: list[data.Query]
    Transaction: list[data.Transaction]


def group_entries_by_type(entries: Entries) -> EntriesByType:
    """Group entries by type.

    Arguments:
        entries: A list of entries to group.

    Returns:
        A namedtuple containing the grouped lists of entries.
    """
    entries_by_type = EntriesByType(
        [], [], [], [], [], [], [], [], [], [], [], []
    )
    for entry in entries:
        getattr(entries_by_type, entry.__class__.__name__).append(entry)
    return entries_by_type
