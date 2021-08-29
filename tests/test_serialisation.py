# pylint: disable=missing-docstring
import datetime
from typing import FrozenSet
from typing import Optional
from typing import Tuple

import pytest
from beancount.core.amount import A
from beancount.core.amount import Amount
from beancount.core.data import Balance
from beancount.core.data import CostSpec
from beancount.core.data import create_simple_posting
from beancount.core.data import Note
from beancount.core.data import Posting
from beancount.core.data import Transaction
from beancount.core.number import D
from beancount.core.number import MISSING
from flask.json import loads

from fava.core.charts import dumps
from fava.core.file import _format_entry
from fava.helpers import FavaAPIException
from fava.serialisation import deserialise
from fava.serialisation import deserialise_posting
from fava.serialisation import extract_tags_links
from fava.serialisation import serialise


def test_serialise() -> None:
    assert serialise(None) is None
    txn = Transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [],
    )
    create_simple_posting(txn, "Assets:ETrade:Cash", "100", "USD")
    create_simple_posting(txn, "Assets:ETrade:GLD", None, None)

    json_txn = {
        "date": "2017-12-12",
        "flag": "*",
        "meta": {},
        "narration": "asdfasd #tag ^link",
        "payee": "Test3",
        "type": "Transaction",
        "postings": [
            {"account": "Assets:ETrade:Cash", "amount": "100 USD"},
            {"account": "Assets:ETrade:GLD", "amount": ""},
        ],
    }

    serialised = loads(dumps(serialise(txn)))
    assert serialised == json_txn

    txn = txn._replace(payee="")
    json_txn["payee"] = ""
    serialised = loads(dumps(serialise(txn)))
    assert serialised == json_txn

    txn = txn._replace(payee=None)
    serialised = loads(dumps(serialise(txn)))
    assert serialised == json_txn


@pytest.mark.parametrize(
    "amount_cost_price,amount_string",
    [
        ((A("100 USD"), None, None), "100 USD"),
        (
            (
                A("100 USD"),
                CostSpec(D("10"), None, "EUR", None, None, False),
                None,
            ),
            "100 USD {10 EUR}",
        ),
        (
            (
                A("100 USD"),
                CostSpec(D("10"), None, "EUR", None, None, False),
                A("11 EUR"),
            ),
            "100 USD {10 EUR} @ 11 EUR",
        ),
        ((A("100 USD"), None, A("11 EUR")), "100 USD @ 11 EUR"),
        (
            (
                A("100 USD"),
                CostSpec(MISSING, None, MISSING, None, None, False),
                None,
            ),
            "100 USD {}",
        ),
    ],
)
def test_serialise_posting(
    amount_cost_price: Tuple[Amount, Optional[CostSpec], Amount],
    amount_string: str,
) -> None:
    pos = Posting("Assets", *amount_cost_price, None, None)
    json = {"account": "Assets", "amount": amount_string}
    assert loads(dumps(serialise(pos))) == json
    assert deserialise_posting(json) == pos


@pytest.mark.parametrize(
    "amount_cost_price,amount_string",
    [
        ((A("100 USD"), None, None), "10*10 USD"),
        ((A("130 USD"), None, None), "100+50 - 20 USD"),
        ((A("-140 USD"), None, None), "-1400 / 10 USD"),
        ((A("10 USD"), None, A("1 EUR")), "10 USD @@ 10 EUR"),
        (
            (A("7 USD"), None, A("1.428571428571428571428571429 EUR")),
            "7 USD @@ 10 EUR",
        ),
        ((A("0 USD"), None, A("0 EUR")), "0 USD @@ 0 EUR"),
    ],
)
def test_deserialise_posting(
    amount_cost_price: Tuple[Amount, Optional[CostSpec], Amount],
    amount_string: str,
) -> None:
    """Roundtrip is not possible here due to total price or calculation."""
    pos = Posting("Assets", *amount_cost_price, None, None)
    json = {"account": "Assets", "amount": amount_string}
    assert deserialise_posting(json) == pos


def test_deserialise_posting_and_format(snapshot) -> None:
    txn = Transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [
            deserialise_posting({"account": "Assets", "amount": "10"}),
            deserialise_posting({"account": "Assets", "amount": "10 EUR @"}),
        ],
    )
    snapshot(_format_entry(txn, 61, 2))


def test_serialise_balance() -> None:
    bal = Balance(
        {},
        datetime.date(2019, 9, 17),
        "Assets:ETrade:Cash",
        A("0.1234567891011121314151617 CHF"),
        None,
        None,
    )

    json = {
        "date": "2019-09-17",
        "amount": {"currency": "CHF", "number": "0.1234567891011121314151617"},
        "diff_amount": None,
        "meta": {},
        "tolerance": None,
        "account": "Assets:ETrade:Cash",
        "type": "Balance",
    }

    serialised = loads(dumps(serialise(bal)))

    assert serialised == json


def test_deserialise() -> None:
    postings = [
        {"account": "Assets:ETrade:Cash", "amount": "100 USD"},
        {"account": "Assets:ETrade:GLD"},
    ]
    json_txn = {
        "type": "Transaction",
        "date": "2017-12-12",
        "flag": "*",
        "payee": "Test3",
        "narration": "asdfasd #tag ^link",
        "meta": {},
        "postings": postings,
    }

    txn = Transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [],
    )
    create_simple_posting(txn, "Assets:ETrade:Cash", "100", "USD")
    txn.postings.append(
        Posting("Assets:ETrade:GLD", MISSING, None, None, None, None)
    )
    assert deserialise(json_txn) == txn

    with pytest.raises(FavaAPIException):
        deserialise({})

    with pytest.raises(FavaAPIException):
        deserialise({"type": "NoEntry"})


def test_deserialise_balance() -> None:
    json_bal = {
        "type": "Balance",
        "date": "2017-12-12",
        "account": "Assets:ETrade:Cash",
        "amount": {"number": "100", "currency": "USD"},
        "meta": {},
    }
    bal = Balance(
        {},
        datetime.date(2017, 12, 12),
        "Assets:ETrade:Cash",
        A("100 USD"),
        None,
        None,
    )
    assert deserialise(json_bal) == bal


def test_deserialise_note() -> None:
    json_note = {
        "type": "Note",
        "date": "2017-12-12",
        "account": "Assets:ETrade:Cash",
        "comment": 'This is some comment or note""',
        "meta": {},
    }
    note = Note(
        {},
        datetime.date(2017, 12, 12),
        "Assets:ETrade:Cash",
        "This is some comment or note",
    )
    assert deserialise(json_note) == note


def test_extract_tags_links() -> None:
    assert extract_tags_links("notag") == ("notag", frozenset(), frozenset())
    extracted1: Tuple[str, FrozenSet[str], FrozenSet[str]] = (
        "Some text",
        frozenset(["tag"]),
        frozenset(),
    )
    assert extract_tags_links("Some text #tag") == extracted1
    assert extract_tags_links("Some text ^link") == (
        "Some text",
        frozenset(),
        frozenset(["link"]),
    )

    extracted2 = ("Some text", frozenset(["tag", "tag2"]), frozenset(["link"]))
    assert extract_tags_links("Some text #tag #tag2 ^link") == extracted2
    assert extract_tags_links("Some text#tag#tag2 ^link") == (
        "Some text#tag#tag2",
        frozenset(),
        frozenset(["link"]),
    )
    assert extract_tags_links("Some text#tag#tag2^link") == (
        "Some text#tag#tag2^link",
        frozenset(),
        frozenset(),
    )
    assert extract_tags_links("#tag") == ("", frozenset(["tag"]), frozenset())
