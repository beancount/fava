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


class InvalidAmountError(FavaAPIError):
    """Invalid amount."""

    def __init__(self, amount: str) -> None:
        super().__init__(f"Invalid amount: {amount}")


@singledispatch
def serialise(entry: Directive | Posting) -> Any:
    """Serialise an entry or posting."""
    if not isinstance(entry, Directive):  # pragma: no cover
        msg = f"Unsupported object {entry}"
        raise TypeError(msg)
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

    ret: dict[str, Any] = {"account": posting.account, "amount": position_str}
    if posting.meta:
        ret["meta"] = copy(posting.meta)
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
        meta=posting.get("meta", {}) or None,
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
