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
    parse_numerical_expression,
    deserialise_posting,
)


def test_parse_numerical_expression():
    assert parse_numerical_expression("0") == D("0")
    assert parse_numerical_expression("5") == D("5")
    assert parse_numerical_expression("0.01") == D("0.01")
    assert parse_numerical_expression("12.345") == D("12.345")
    assert parse_numerical_expression(".12") == D(".12")
    assert parse_numerical_expression("-3") == D("-3")
    assert parse_numerical_expression("1+2 + 3") == D("6")
    assert parse_numerical_expression("4-1 + 2") == D("5")
    assert parse_numerical_expression("2*3 * 1") == D("6")
    assert parse_numerical_expression("5/2") == D("2.5")
    assert parse_numerical_expression("6/2") == D("3")
    assert parse_numerical_expression("1.5 + 2 * -3 - 3 / 2") == D("-6")
    with pytest.raises(FavaAPIException):
        parse_numerical_expression("a")
    with pytest.raises(FavaAPIException):
        parse_numerical_expression("print('a')")
    with pytest.raises(FavaAPIException):
        parse_numerical_expression("3**2")


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
            (A("100 USD"), Cost(D("10"), "EUR", None, None), None),
            "100 USD {10 EUR}",
        ),
        (
            (A("100 USD"), Cost(D("10"), "EUR", None, None), A("11 EUR")),
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
def test_serialise_posting(amount_cost_price, amount_string):
    pos = Posting("Assets", *amount_cost_price, None, None)
    json = {"account": "Assets", "amount": amount_string}
    assert loads(dumps(serialise(pos))) == json
    assert deserialise_posting(json) == pos


@pytest.mark.parametrize(
    "amount_cost_price,amount_string",
    [
        ((A("10 USD"), None, A("1 EUR")), "10 USD @@ 10 EUR"),
        (
            (A("7 USD"), None, A("1.428571428571428571428571429 EUR")),
            "7 USD @@ 10 EUR",
        ),
        ((A("0 USD"), None, A("0 EUR")), "0 USD @@ 0 EUR"),
    ],
)
def test_deserialise_posting(amount_cost_price, amount_string):
    """Cases where a roundtrip is not possible due to total price."""
    pos = Posting("Assets", *amount_cost_price, None, None)
    json = {"account": "Assets", "amount": amount_string}
    assert deserialise_posting(json) == pos


def test_serialise_balance(app):
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

    with app.test_request_context():
        serialised = loads(dumps(serialise(bal)))

    assert serialised == json


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


def test_deserialise_numerical_expression():
    postings = [
        {"account": "Assets:ETrade:Cash", "amount": "100+50 - 20 USD"},
        {"account": "Assets:ETrade:Bank", "amount": "-1400/10 USD"},
        {"account": "Assets:ETrade:Foreign", "amount": "2*5 USD"},
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
    create_simple_posting(txn, "Assets:ETrade:Cash", "130", "USD")
    create_simple_posting(txn, "Assets:ETrade:Bank", "-140", "USD")
    create_simple_posting(txn, "Assets:ETrade:Foreign", "10", "USD")
    assert deserialise(json_txn) == txn


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
