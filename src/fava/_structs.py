"""msgspec Structs used in serialisation."""

from __future__ import annotations

import datetime  # noqa: TC003 - needed for msgspec
from decimal import Decimal  # noqa: TC003 - needed for msgspec

from beancount.core.data import Booking  # noqa: TC002 - needed for msgspec
from msgspec import Struct

from fava.core.inventory import _Amount  # noqa: TC001 - needed for msgspec

try:
    from typing import dataclass_transform
except ImportError:  # pragma: no cover
    from typing_extensions import dataclass_transform


# mark it so that ty realizes the subclasses are frozen as well:
@dataclass_transform(frozen_default=True)
class EntryStruct(Struct, frozen=True, tag_field="t", kw_only=True):
    """msgspec Struct representations of entries."""

    date: datetime.date
    meta: dict[str, str | bool | _Amount]
    # Only present when sending entries to the frontend.
    entry_hash: str = ""


class Balance(EntryStruct):
    account: str
    amount: _Amount
    diff_amount: _Amount | None = None
    tolerance: Decimal | None = None


class Close(EntryStruct):
    account: str


class Commodity(EntryStruct):
    currency: str


class Custom(EntryStruct):
    type: str
    values: list[str | bool | datetime.date | Decimal | _Amount]


class Document(EntryStruct):
    account: str
    filename: str
    tags: frozenset[str] | None = None
    links: frozenset[str] | None = None


class Event(EntryStruct):
    type: str
    description: str


class Note(EntryStruct):
    account: str
    comment: str
    tags: frozenset[str] | None = None
    links: frozenset[str] | None = None


class Open(EntryStruct):
    account: str
    currencies: list[str] | None
    booking: Booking | None = None


class Pad(EntryStruct):
    account: str
    source_account: str


class Price(EntryStruct):
    currency: str
    amount: _Amount


class Query(EntryStruct):
    name: str
    query_string: str


class Posting(Struct, frozen=True, kw_only=True, omit_defaults=True):
    account: str
    amount: str = ""
    flag: str = ""
    meta: dict[str, str | bool | _Amount] | None = None


class Transaction(EntryStruct):
    flag: str
    narration: str
    postings: list[Posting]
    payee: str = ""
    tags: frozenset[str] = frozenset()
    links: frozenset[str] = frozenset()
