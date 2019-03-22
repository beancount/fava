# pylint: disable=missing-docstring

import datetime

from beancount.core.data import (
    Transaction,
    create_simple_posting,
    Balance,
    Note,
    Posting,
)
from beancount.core.amount import A
from beancount.core.number import D, MISSING
from beancount.core.position import Cost
from beancount.core.data import CostSpec
from flask.json import dumps, loads
import pytest

from fava.core.helpers import FavaAPIException
from fava.serialisation import (
    serialise,
    deserialise,
    extract_tags_links,
    parse_number,
    deserialise_posting,
)


def test_parse_number():
    assert parse_number("5/2") == D("2.5")
    assert parse_number("5") == D("5")
    assert parse_number("12.345") == D("12.345")


def test_serialise(app):
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

    with app.test_request_context():
        serialised = loads(dumps(serialise(txn)))
    assert serialised == json_txn


@pytest.mark.parametrize(
    "pos,amount",
    [
        ((A("100 USD"), None, None, None, None), "100 USD"),
        (
            (A("100 USD"), Cost(D("10"), "EUR", None, None), None, None, None),
            "100 USD {10 EUR}",
        ),
        (
            (
                A("100 USD"),
                Cost(D("10"), "EUR", None, None),
                A("11 EUR"),
                None,
                None,
            ),
            "100 USD {10 EUR} @ 11 EUR",
        ),
        ((A("100 USD"), None, A("11 EUR"), None, None), "100 USD @ 11 EUR"),
        (
            (
                A("100 USD"),
                CostSpec(MISSING, None, MISSING, None, None, False),
                None,
                None,
                None,
            ),
            "100 USD {}",
        ),
    ],
)
def test_serialise_posting(pos, amount):
    pos = Posting("Assets:ETrade:Cash", *pos)
    json = {"account": "Assets:ETrade:Cash", "amount": amount}
    assert loads(dumps(serialise(pos))) == json
    assert deserialise_posting(json) == pos


def test_deserialise():
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
    create_simple_posting(txn, "Assets:ETrade:GLD", None, None)
    assert deserialise(json_txn) == txn

    with pytest.raises(KeyError):
        deserialise({})

    with pytest.raises(FavaAPIException):
        deserialise({"type": "NoEntry"})


def test_deserialise_balance():
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


def test_deserialise_note():
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


def test_extract_tags_links():
    assert extract_tags_links("notag") == ("notag", frozenset(), frozenset())
    extracted1 = ("Some text", frozenset(["tag"]), frozenset())
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
