"""(De)serialisation of entries.

When adding entries, these are saved via the JSON API - using the functionality
of this module to obtain the appropriate data structures from
`beancount.core.data`. Similarly, for the full entry completion, a JSON
representation of the entry is provided.

This is not intended to work well enough for full roundtrips yet.
"""
from __future__ import annotations

import datetime
import functools
import re
from typing import Any

from beancount.core.amount import Amount
from beancount.core.data import Balance
from beancount.core.data import Close
from beancount.core.data import Commodity
from beancount.core.data import Custom
from beancount.core.data import Directive
from beancount.core.data import Document
from beancount.core.data import EMPTY_SET
from beancount.core.data import Event
from beancount.core.data import Note
from beancount.core.data import Open
from beancount.core.data import Pad
from beancount.core.data import Posting
from beancount.core.data import Price
from beancount.core.data import Query
from beancount.core.data import Transaction
from beancount.core.number import D
from beancount.core.position import to_string as position_to_string
from beancount.parser.parser import parse_string

from fava.helpers import FavaAPIException
from fava.util.date import parse_date


def extract_tags_links(
    string: str,
) -> tuple[str | None, frozenset[str], frozenset[str]]:
    """Extract tags and links from a narration string.

    Args:
        string: A string, possibly containing tags (`#tag`) and links
        (`^link`).

    Returns:
        A triple (new_string, tags, links) where `new_string` is `string`
        stripped of tags and links.
    """

    if string is None:
        return None, EMPTY_SET, EMPTY_SET

    tags = re.findall(r"(?:^|\s)#([A-Za-z0-9\-_/.]+)", string)
    links = re.findall(r"(?:^|\s)\^([A-Za-z0-9\-_/.]+)", string)
    new_string = re.sub(r"(?:^|\s)[#^]([A-Za-z0-9\-_/.]+)", "", string).strip()

    return new_string, frozenset(tags), frozenset(links)


ENTRY_TYPES = (
    Open,
    Close,
    Commodity,
    Pad,
    Balance,
    Transaction,
    Note,
    Event,
    Query,
    Price,
    Document,
    Custom,
)


@functools.singledispatch
def serialise(entry: Directive | Posting) -> Any:
    """Serialise an entry or posting."""
    assert isinstance(entry, ENTRY_TYPES), f"Unsupported object {entry}"
    ret = entry._asdict()
    ret["type"] = entry.__class__.__name__
    return ret


@serialise.register
def _(entry: Transaction) -> Any:
    """Serialise an entry."""
    ret = entry._asdict()
    ret["type"] = "Transaction"
    ret["payee"] = entry.payee or ""
    if entry.tags:
        ret["narration"] += " " + " ".join(["#" + n for n in entry.tags])
    if entry.links:
        ret["narration"] += " " + " ".join(["^" + n for n in entry.links])
    del ret["links"]
    del ret["tags"]
    ret["postings"] = list(map(serialise, entry.postings))
    return ret


@serialise.register
def _(entry: Balance) -> Any:
    """Serialise an entry."""
    ret = entry._asdict()
    ret["type"] = "Balance"
    amt = ret["amount"]
    ret["amount"] = {"number": str(amt.number), "currency": amt.currency}
    return ret


@serialise.register
def _(posting: Posting) -> Any:
    """Serialise a posting."""
    if isinstance(posting.units, Amount):
        position_str = position_to_string(posting)
    else:
        position_str = ""

    if posting.price is not None:
        position_str += f" @ {posting.price.to_string()}"
    return {"account": posting.account, "amount": position_str}


def deserialise_posting(posting: Any) -> Posting:
    """Parse JSON to a Beancount Posting."""
    amount = posting.get("amount", "")
    entries, errors, _ = parse_string(
        f'2000-01-01 * "" ""\n Assets:Account {amount}'
    )
    if errors:
        raise FavaAPIException(f"Invalid amount: {amount}")
    txn = entries[0]
    assert isinstance(txn, Transaction)
    pos = txn.postings[0]
    return pos._replace(account=posting["account"], meta=None)


def deserialise(json_entry: Any) -> Directive:
    """Parse JSON to a Beancount entry.

    Args:
        json_entry: The entry.

    Raises:
        KeyError: if one of the required entry fields is missing.
        FavaAPIException: if the type of the given entry is not supported.
    """
    date = parse_date(json_entry.get("date", ""))[0]
    if not isinstance(date, datetime.date):
        raise FavaAPIException("Invalid entry date.")
    if json_entry["type"] == "Transaction":
        narration, tags, links = extract_tags_links(json_entry["narration"])
        postings = [deserialise_posting(pos) for pos in json_entry["postings"]]
        return Transaction(
            json_entry["meta"],
            date,
            json_entry.get("flag", ""),
            json_entry.get("payee", ""),
            narration or "",
            tags,
            links,
            postings,
        )
    if json_entry["type"] == "Balance":
        raw_amount = json_entry["amount"]
        amount = Amount(D(str(raw_amount["number"])), raw_amount["currency"])

        return Balance(
            json_entry["meta"], date, json_entry["account"], amount, None, None
        )
    if json_entry["type"] == "Note":
        comment = json_entry["comment"].replace('"', "")
        return Note(json_entry["meta"], date, json_entry["account"], comment)
    raise FavaAPIException("Unsupported entry type.")
