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
from functools import singledispatch
from typing import Any

from beancount.parser.parser import parse_string

from fava.beans import create
from fava.beans.abc import Amount
from fava.beans.abc import Balance
from fava.beans.abc import Directive
from fava.beans.abc import Posting
from fava.beans.abc import Transaction
from fava.beans.helpers import replace
from fava.beans.str import to_string
from fava.helpers import FavaAPIError
from fava.util.date import parse_date


@singledispatch
def serialise(entry: Directive | Posting) -> Any:
    """Serialise an entry or posting."""
    if not isinstance(entry, Directive):
        raise TypeError(f"Unsupported object {entry}")
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["t"] = entry.__class__.__name__
    return ret


@serialise.register(Transaction)
def _(entry: Transaction) -> Any:
    """Serialise an entry."""
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["meta"] = copy(entry.meta)
    ret["meta"].pop("__tolerances__", None)
    ret["t"] = "Transaction"
    ret["payee"] = entry.payee or ""
    ret["postings"] = list(map(serialise, entry.postings))
    return ret


@serialise.register(Balance)
def _(entry: Balance) -> Any:
    """Serialise an entry."""
    ret = entry._asdict()  # type: ignore[attr-defined]
    ret["t"] = "Balance"
    amt = ret["amount"]
    ret["amount"] = {"number": str(amt.number), "currency": amt.currency}
    return ret


@serialise.register(Posting)
def _(posting: Posting) -> Any:
    """Serialise a posting."""
    position_str = (
        to_string(posting) if isinstance(posting.units, Amount) else ""
    )

    if posting.price is not None:
        position_str += f" @ {to_string(posting.price)}"
    return {"account": posting.account, "amount": position_str}


def deserialise_posting(posting: Any) -> Posting:
    """Parse JSON to a Beancount Posting."""
    amount = posting.get("amount", "")
    entries, errors, _ = parse_string(
        f'2000-01-01 * "" ""\n Assets:Account {amount}',
    )
    if errors:
        raise FavaAPIError(f"Invalid amount: {amount}")
    txn = entries[0]
    if not isinstance(txn, Transaction):
        raise TypeError("Expected transaction")
    pos = txn.postings[0]
    return replace(pos, account=posting["account"], meta=None)


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
        raise FavaAPIError("Invalid entry date.")
    if json_entry["t"] == "Transaction":
        postings = [deserialise_posting(pos) for pos in json_entry["postings"]]
        return create.transaction(
            json_entry["meta"],
            date,
            json_entry.get("flag", ""),
            json_entry.get("payee", ""),
            json_entry["narration"] or "",
            frozenset(json_entry["tags"]),
            frozenset(json_entry["links"]),
            postings,
        )
    if json_entry["t"] == "Balance":
        raw_amount = json_entry["amount"]
        amount = create.amount(
            f"{raw_amount['number']} {raw_amount['currency']}",
        )

        return create.balance(
            json_entry["meta"],
            date,
            json_entry["account"],
            amount,
        )
    if json_entry["t"] == "Note":
        comment = json_entry["comment"].replace('"', "")
        return create.note(
            json_entry["meta"],
            date,
            json_entry["account"],
            comment,
        )
    raise FavaAPIError("Unsupported entry type.")
