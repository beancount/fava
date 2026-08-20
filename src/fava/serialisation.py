"""(De)serialisation of entries.

When adding entries, these are saved via the JSON API - using the functionality
of this module to obtain the appropriate data structures from
`beancount.core.data`. Similarly, for the full entry completion, a JSON
representation of the entry is provided.

This is not intended to work well enough for full roundtrips yet.
"""

from __future__ import annotations

import datetime
from copy import copy
from decimal import Decimal
from functools import singledispatch
from typing import Any
from typing import TYPE_CHECKING

from beancount.parser.parser import parse_string

from fava.beans import create
from fava.beans.abc import Balance
from fava.beans.abc import Custom
from fava.beans.abc import Directive
from fava.beans.abc import Posting
from fava.beans.abc import Price
from fava.beans.abc import Transaction
from fava.beans.funcs import hash_entry
from fava.beans.helpers import replace
from fava.beans.str import to_string
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Meta
    from fava.beans.abc import MetaValue


class InvalidAmountError(FavaAPIError):
    """Invalid amount."""

    def __init__(self, amount: str) -> None:
        super().__init__(f"Invalid amount: {amount}")


def _serialise_meta_value(value: MetaValue) -> Any:
    """Serialise a single metadata value, tagging Decimal and Amount."""
    if isinstance(value, Decimal):
        return {"t": "Decimal", "value": str(value)}
    if hasattr(value, "number") and hasattr(value, "currency"):
        return {
            "t": "Amount",
            "number": str(value.number),
            "currency": value.currency,
        }
    return value


def _serialise_meta(meta: Meta | None) -> dict[str, Any]:
    """Serialise a metadata mapping, tagging Decimal and Amount values."""
    if not meta:
        return {}
    return {key: _serialise_meta_value(value) for key, value in meta.items()}


def _deserialise_meta_value(value: Any) -> Any:
    """Deserialise a single metadata value, restoring Decimal and Amount."""
    if isinstance(value, dict):
        tag = value.get("t")
        if tag == "Decimal":
            return Decimal(value["value"])
        if tag == "Amount":
            return create.amount(Decimal(value["number"]), value["currency"])
    return value


def _deserialise_meta(meta: Any) -> dict[str, Any]:
    """Deserialise a metadata mapping, restoring Decimal and Amount values."""
    if not meta:
        return {}
    return {key: _deserialise_meta_value(value) for key, value in meta.items()}


@singledispatch
def serialise(entry: Directive | Posting) -> Any:
    """Serialise an entry or posting."""
    if not isinstance(entry, Directive):  # pragma: no cover
        msg = f"Unsupported object {entry}"
        raise TypeError(msg)
    ret = entry._asdict()  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    ret["meta"] = _serialise_meta(entry.meta)
    ret["entry_hash"] = hash_entry(entry)
    ret["t"] = entry.__class__.__name__
    return ret


@serialise.register(Transaction)
def _(entry: Transaction) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    ret["meta"] = copy(entry.meta)
    ret["meta"].pop("__tolerances__", None)
    ret["meta"] = _serialise_meta(ret["meta"])
    ret["t"] = "Transaction"
    ret["entry_hash"] = hash_entry(entry)
    ret["payee"] = entry.payee or ""
    ret["postings"] = list(map(serialise, entry.postings))
    return ret


@serialise.register(Custom)
def _(entry: Custom) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    ret["meta"] = _serialise_meta(entry.meta)
    ret["t"] = "Custom"
    ret["entry_hash"] = hash_entry(entry)
    ret["values"] = [v.value for v in entry.values]
    return ret


@serialise.register(Balance)
def _(entry: Balance) -> Any:
    amount = entry.amount
    return {
        "t": "Balance",
        "entry_hash": hash_entry(entry),
        "date": entry.date,
        "meta": _serialise_meta(entry.meta),
        "account": entry.account,
        "amount": {"number": str(amount.number), "currency": amount.currency},
        "diff_amount": entry.diff_amount,
        "tolerance": entry.tolerance,
    }


@serialise.register(Price)
def _(entry: Price) -> Any:
    amount = entry.amount
    return {
        "t": "Price",
        "entry_hash": hash_entry(entry),
        "date": entry.date,
        "meta": _serialise_meta(entry.meta),
        "currency": entry.currency,
        "amount": {"number": str(amount.number), "currency": amount.currency},
    }


@serialise.register(Posting)
def _(posting: Posting) -> Any:
    position_str = to_string(posting) if posting.units is not None else ""

    if posting.price is not None:
        position_str += f" @ {to_string(posting.price)}"

    ret: dict[str, Any] = {"account": posting.account, "amount": position_str}
    if posting.meta:
        ret["meta"] = _serialise_meta(posting.meta)
    return ret


def deserialise_posting(posting: Any) -> Posting:
    """Parse JSON to a Beancount Posting."""
    amount = posting.get("amount", "")
    entries, errors, _ = parse_string(
        f'2000-01-01 * "" ""\n Assets:Account {amount}',
    )
    if errors:
        raise InvalidAmountError(amount)
    txn = entries[0]
    if not isinstance(txn, Transaction):  # pragma: no cover
        msg = "Expected transaction"
        raise TypeError(msg)
    pos = txn.postings[0]
    return replace(
        pos,
        account=posting["account"],
        meta=_deserialise_meta(posting.get("meta")) or None,
    )


def deserialise(json_entry: Any) -> Directive:
    """Parse JSON to a Beancount entry.

    Args:
        json_entry: The entry.

    Raises:
        KeyError: if one of the required entry fields is missing.
        FavaAPIError: if the type of the given entry is not supported.
    """
    try:
        date = datetime.date.fromisoformat(json_entry.get("date", ""))
    except ValueError as error:
        msg = "Invalid entry date."
        raise FavaAPIError(msg) from error
    if json_entry["t"] == "Transaction":
        postings = [deserialise_posting(pos) for pos in json_entry["postings"]]
        return create.transaction(
            meta=_deserialise_meta(json_entry["meta"]),
            date=date,
            flag=json_entry.get("flag", ""),
            payee=json_entry.get("payee", ""),
            narration=json_entry["narration"] or "",
            tags=frozenset(json_entry["tags"]),
            links=frozenset(json_entry["links"]),
            postings=postings,
        )
    if json_entry["t"] == "Balance":
        raw_amount = json_entry["amount"]
        amount = create.amount(
            Decimal(raw_amount["number"]), raw_amount["currency"]
        )

        return create.balance(
            meta=_deserialise_meta(json_entry["meta"]),
            date=date,
            account=json_entry["account"],
            amount=amount,
        )
    if json_entry["t"] == "Note":
        comment = json_entry["comment"].replace('"', "")
        return create.note(
            meta=_deserialise_meta(json_entry["meta"]),
            date=date,
            account=json_entry["account"],
            comment=comment,
        )
    msg = "Unsupported entry type."
    raise FavaAPIError(msg)
