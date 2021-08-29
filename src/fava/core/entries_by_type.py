"""Entries grouped by type."""
from typing import List
from typing import NamedTuple

from beancount.core.data import Balance
from beancount.core.data import Close
from beancount.core.data import Commodity
from beancount.core.data import Custom
from beancount.core.data import Document
from beancount.core.data import Entries
from beancount.core.data import Event
from beancount.core.data import Note
from beancount.core.data import Open
from beancount.core.data import Pad
from beancount.core.data import Price
from beancount.core.data import Query
from beancount.core.data import Transaction


class EntriesByType(NamedTuple):
    """Entries grouped by type."""

    Balance: List[Balance]
    Close: List[Close]
    Commodity: List[Commodity]
    Custom: List[Custom]
    Document: List[Document]
    Event: List[Event]
    Note: List[Note]
    Open: List[Open]
    Pad: List[Pad]
    Price: List[Price]
    Query: List[Query]
    Transaction: List[Transaction]


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
