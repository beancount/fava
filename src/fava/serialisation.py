"""(De)serialisation of entries.

When adding entries, these are saved via the JSON API - using the functionality
of this module to obtain the appropriate data structures from
`beancount.core.data`. Similarly, for the full entry completion, a JSON
representation of the entry is provided.

This is not intended to work well enough for full roundtrips yet.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Mapping
from decimal import Decimal
from functools import singledispatch
from typing import Any

from beancount.core import amount
from beancount.parser.parser import parse_string

from fava._structs import Balance
from fava._structs import Close
from fava._structs import Commodity
from fava._structs import Custom
from fava._structs import Document
from fava._structs import Event
from fava._structs import Note
from fava._structs import Open
from fava._structs import Pad
from fava._structs import Posting
from fava._structs import Price
from fava._structs import Query
from fava._structs import Transaction
from fava.beans import abc
from fava.beans import create
from fava.beans import protocols
from fava.beans.funcs import hash_entry
from fava.beans.helpers import replace
from fava.beans.str import to_string
from fava.core.inventory import _Amount
from fava.helpers import FavaAPIError


class InvalidAmountError(FavaAPIError):
    """Invalid amount."""

    def __init__(self, amount: str) -> None:
        super().__init__(f"Invalid amount: {amount}")


SerialisableValue = (
    abc.Directive
    | amount.Amount
    | protocols.Amount
    | datetime.date
    | str
    | int
    | Decimal
    | Mapping[str, "SerialisableValue"]
)


@singledispatch
def serialise(o: SerialisableValue) -> object:
    """Map a value so that it can be serialised to JSON."""
    # Serialise a value that does not need any special handling
    return o


def _serialise_dict(o: Mapping[str, SerialisableValue]) -> dict[str, Any]:
    return {k: serialise(v) for k, v in o.items()}


serialise.register(dict, _serialise_dict)


@serialise.register
def _(o: amount.Amount) -> _Amount:
    return _Amount.from_amount(o)


@serialise.register
def _(o: abc.Balance) -> Balance:
    return Balance(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
        amount=_Amount.from_amount(o.amount),
        diff_amount=_Amount.from_amount(o.diff_amount),
        tolerance=o.tolerance,
    )


@serialise.register
def _(o: abc.Close) -> Close:
    return Close(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
    )


@serialise.register
def _(o: abc.Commodity) -> Commodity:
    return Commodity(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        currency=o.currency,
    )


@serialise.register
def _(o: abc.Custom) -> Custom:
    return Custom(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        type=o.type,
        values=[serialise(v.value) for v in o.values],  # type: ignore[misc]  # ty: ignore[invalid-argument-type]
    )


@serialise.register
def _(o: abc.Document) -> Document:
    return Document(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
        filename=o.filename,
        tags=o.tags,
        links=o.links,
    )


@serialise.register
def _(o: abc.Event) -> Event:
    return Event(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        type=o.type,
        description=o.description,
    )


@serialise.register
def _(o: abc.Note) -> Note:
    return Note(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
        comment=o.comment,
        tags=o.tags,
        links=o.links,
    )


@serialise.register
def _(o: abc.Open) -> Open:
    return Open(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
        currencies=list(o.currencies) if o.currencies else None,
        booking=o.booking,
    )


@serialise.register
def _(o: abc.Pad) -> Pad:
    return Pad(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        account=o.account,
        source_account=o.source_account,
    )


@serialise.register
def _(o: abc.Price) -> Price:
    return Price(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        currency=o.currency,
        amount=_Amount.from_amount(o.amount),
    )


@serialise.register
def _(o: abc.Query) -> Query:
    return Query(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        name=o.name,
        query_string=o.query_string,
    )


def _serialise_posting(o: abc.Posting) -> Posting:
    position_str = to_string(o) if o.units is not None else ""

    if o.price is not None:
        position_str += f" @ {to_string(o.price)}"

    return Posting(
        account=o.account,
        amount=position_str,
        meta=_serialise_dict(o.meta) if o.meta is not None else None,
    )


@serialise.register
def _(o: abc.Transaction) -> Transaction:
    return Transaction(
        entry_hash=hash_entry(o),
        date=o.date,
        meta=_serialise_dict(o.meta),
        flag=o.flag,
        narration=o.narration,
        postings=list(map(_serialise_posting, o.postings)),
        payee=o.payee or "",
        tags=o.tags,
        links=o.links,
    )


# Matches a bare decimal number, e.g. "10.10" or "-5", as sent by the
# frontend for metadata values that are Decimal instances there.
_DECIMAL_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _deserialise_meta_value(
    o: str | bool | _Amount,  # noqa: FBT001
) -> str | bool | Decimal | protocols.Amount:
    """Deserialise a single metadata value, restoring Decimal and Amount."""
    if isinstance(o, str) and _DECIMAL_RE.fullmatch(o):
        return Decimal(o)
    if isinstance(o, _Amount):
        return create.amount(o.number, o.currency)
    return o


def _deserialise_meta(
    o: Mapping[str, str | bool | _Amount],
) -> Mapping[str, str | bool | Decimal | protocols.Amount]:
    """Deserialise a metadata mapping, restoring Decimal and Amount values."""
    return {key: _deserialise_meta_value(value) for key, value in o.items()}


def _deserialise_posting(posting: Posting) -> abc.Posting:
    """Parse JSON to a Beancount Posting."""
    entries, errors, _ = parse_string(
        f'2000-01-01 * "" ""\n Assets:Account {posting.amount}',
    )
    if errors:
        raise InvalidAmountError(posting.amount)
    txn = entries[0]
    if not isinstance(txn, abc.Transaction):  # pragma: no cover
        msg = "Expected transaction"
        raise TypeError(msg)
    pos = txn.postings[0]
    return replace(
        pos,
        account=posting.account,
        meta=_deserialise_meta(posting.meta) if posting.meta else None,
    )


def deserialise(entry: Balance | Note | Transaction) -> abc.Directive:
    """Convert an entry received from the frontend to a Beancount entry."""
    if isinstance(entry, Transaction):
        return create.transaction(
            meta=_deserialise_meta(entry.meta),
            date=entry.date,
            flag=entry.flag,
            payee=entry.payee,
            narration=entry.narration,
            tags=entry.tags,
            links=entry.links,
            postings=[_deserialise_posting(pos) for pos in entry.postings],
        )
    if isinstance(entry, Balance):
        return create.balance(
            meta=_deserialise_meta(entry.meta),
            date=entry.date,
            account=entry.account,
            amount=create.amount(entry.amount.number, entry.amount.currency),
        )

    comment = entry.comment.replace('"', "")
    return create.note(
        meta=_deserialise_meta(entry.meta),
        date=entry.date,
        account=entry.account,
        comment=comment,
    )
