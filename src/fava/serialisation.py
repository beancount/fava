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

from fava.beans import create
from fava.beans.load import load_string
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
from fava.util.date import parse_date


class InvalidAmountError(FavaAPIError):
    """Invalid amount."""

    def __init__(self, amount: str) -> None:
        super().__init__(f"Invalid amount: {amount}")


# Internal meta fields that should not be serialised to JSON
_INTERNAL_META_KEYS = {"filename", "lineno", "hash", "__tolerances__"}

# Map rustledger type names to standard beancount type names
_TYPE_NAME_MAP = {
    "RLDocument": "Document",
    "RLNote": "Note",
    "RLEvent": "Event",
    "RLQuery": "Query",
    "RLCommodity": "Commodity",
    "RLOpen": "Open",
    "RLClose": "Close",
    "RLPad": "Pad",
}


def _get_entry_type_name(entry: Directive) -> str:
    """Get the canonical entry type name for serialisation."""
    name = entry.__class__.__name__
    return _TYPE_NAME_MAP.get(name, name)


def _clean_meta(meta: dict) -> dict:
    """Remove internal meta fields from a copy of the metadata."""
    result = copy(meta)
    for key in _INTERNAL_META_KEYS:
        result.pop(key, None)
    return result


@singledispatch
def serialise(entry: Directive | Posting) -> Any:
    """Serialise an entry or posting."""
    if not isinstance(entry, Directive):  # pragma: no cover
        msg = f"Unsupported object {entry}"
        raise TypeError(msg)
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = _clean_meta(ret.get("meta", {}))
    ret["entry_hash"] = hash_entry(entry)
    ret["t"] = _get_entry_type_name(entry)
    return ret


@serialise.register(Transaction)
def _(entry: Transaction) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = _clean_meta(entry.meta)
    ret["t"] = "Transaction"
    ret["entry_hash"] = hash_entry(entry)
    ret["payee"] = entry.payee or ""
    ret["postings"] = list(map(serialise, entry.postings))
    return ret


@serialise.register(Custom)
def _(entry: Custom) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = _clean_meta(ret.get("meta", {}))
    ret["t"] = "Custom"
    ret["entry_hash"] = hash_entry(entry)
    ret["values"] = [v.value for v in entry.values]
    return ret


@serialise.register(Balance)
def _(entry: Balance) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = _clean_meta(ret.get("meta", {}))
    ret["t"] = "Balance"
    ret["entry_hash"] = hash_entry(entry)
    amt = ret["amount"]
    ret["amount"] = {"number": str(amt.number), "currency": amt.currency}
    return ret


@serialise.register(Price)
def _(entry: Balance) -> Any:
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = _clean_meta(ret.get("meta", {}))
    ret["t"] = "Price"
    ret["entry_hash"] = hash_entry(entry)
    amt = ret["amount"]
    ret["amount"] = {"number": str(amt.number), "currency": amt.currency}
    return ret


@serialise.register(Posting)
def _(posting: Posting) -> Any:
    position_str = to_string(posting) if posting.units is not None else ""

    if posting.price is not None:
        position_str += f" @ {to_string(posting.price)}"

    ret: dict[str, Any] = {"account": posting.account, "amount": position_str}
    if posting.meta:
        ret["meta"] = copy(posting.meta)
    return ret


_DUMMY_DATE = datetime.date(2000, 1, 1)


def deserialise_posting(posting: Any) -> Posting:
    """Parse JSON to a Beancount Posting."""
    amount = posting.get("amount", "")
    entries, errors, _ = load_string(
        f'2000-01-01 * "" ""\n  Assets:Account {amount}',
    )
    # Raise error if:
    # - No entries were parsed at all
    # - Amount was provided but there's a parse error (not inference warning)
    has_parse_error = any("parse error" in str(e.message).lower() for e in errors)
    if not entries or (amount and has_parse_error):
        raise InvalidAmountError(amount)
    txn = entries[0]
    if not isinstance(txn, Transaction):  # pragma: no cover
        msg = "Expected transaction"
        raise TypeError(msg)
    pos = txn.postings[0]
    # Strip dummy date from cost if present (booking assigns transaction date)
    cost = pos.cost
    if cost is not None and getattr(cost, "date", None) == _DUMMY_DATE:
        cost = replace(cost, date=None)
    return replace(
        pos,
        account=posting["account"],
        meta=posting.get("meta", {}) or None,
        cost=cost,
    )


def deserialise(json_entry: Any) -> Directive:
    """Parse JSON to a Beancount entry.

    Args:
        json_entry: The entry.

    Raises:
        KeyError: if one of the required entry fields is missing.
        FavaAPIError: if the type of the given entry is not supported.
    """
    date = parse_date(json_entry.get("date", ""))[0]
    if not isinstance(date, datetime.date):
        msg = "Invalid entry date."
        raise FavaAPIError(msg)
    if json_entry["t"] == "Transaction":
        postings = [deserialise_posting(pos) for pos in json_entry["postings"]]
        return create.transaction(
            meta=json_entry["meta"],
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
            meta=json_entry["meta"],
            date=date,
            account=json_entry["account"],
            amount=amount,
        )
    if json_entry["t"] == "Note":
        comment = json_entry["comment"].replace('"', "")
        return create.note(
            meta=json_entry["meta"],
            date=date,
            account=json_entry["account"],
            comment=comment,
        )
    msg = "Unsupported entry type."
    raise FavaAPIError(msg)
