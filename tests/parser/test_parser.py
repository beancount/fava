# pylint: disable=missing-docstring

import datetime

import pytest
from beancount.core.data import Booking
from beancount.core.data import Close
from beancount.core.data import Document
from beancount.core.data import EMPTY_SET
from beancount.core.data import Note
from beancount.core.data import Open
from beancount.core.number import D

from fava.parser.parser import PARSER
from fava.parser.parser import ParserState


def _parse_single(line):
    contents = bytes(line, "utf-8")
    tree = PARSER.parse(contents)
    state = ParserState(contents)
    return state.handle_node(tree.root_node.children[0])


def _parse_many(line):
    contents = bytes(line, "utf-8")
    tree = PARSER.parse(contents)
    state = ParserState(contents)
    return list(map(state.handle_node, tree.root_node.children))


DUMMY_DATE = datetime.date(2012, 12, 12)

META = {"filename": None, "lineno": 1}
TEST_PARAMS = [
    (
        "2012-12-12 open Assets:Cash",
        Open(META, DUMMY_DATE, "Assets:Cash", None, None),
    ),
    (
        '2012-12-12 note Assets:Cash "note"',
        Note(META, DUMMY_DATE, "Assets:Cash", "note"),
    ),
    (
        "2012-12-12 open Assets:Cash EUR,USD",
        Open(META, DUMMY_DATE, "Assets:Cash", ["EUR", "USD"], None),
    ),
    (
        '2012-12-12 open Assets:Cash EUR,USD "FIFO"',
        Open(META, DUMMY_DATE, "Assets:Cash", ["EUR", "USD"], Booking.FIFO),
    ),
    (
        '2012-12-12 open Assets:Cash "STRICT"',
        Open(META, DUMMY_DATE, "Assets:Cash", None, Booking.STRICT),
    ),
    ("2012-12-12 close Assets:Cash", Close(META, DUMMY_DATE, "Assets:Cash")),
    (
        "2012-12-12 close Assets:Cash\n key: 10",
        Close(
            {"filename": None, "lineno": 1, "key": D("10")},
            DUMMY_DATE,
            "Assets:Cash",
        ),
    ),
    (
        '2012-12-12 document Assets:Cash "test.csv"',
        Document(
            META, DUMMY_DATE, "Assets:Cash", "test.csv", EMPTY_SET, EMPTY_SET
        ),
    ),
    (
        '2012-12-12 document Assets:Cash "test.csv" #tag',
        Document(
            META,
            DUMMY_DATE,
            "Assets:Cash",
            "test.csv",
            set(["tag"]),
            EMPTY_SET,
        ),
    ),
    (
        '2012-12-12 document Assets:Cash "test.csv" #tag ^link',
        Document(
            META,
            DUMMY_DATE,
            "Assets:Cash",
            "test.csv",
            set(["tag"]),
            set(["link"]),
        ),
    ),
    (
        '2012-12-12 document Assets:Cash "test.csv" #tag\n ^link\n asdf: TRUE',
        Document(
            {"filename": None, "lineno": 1, "asdf": True},
            DUMMY_DATE,
            "Assets:Cash",
            "test.csv",
            set(["tag"]),
            set(["link"]),
        ),
    ),
]


@pytest.mark.parametrize("line,result", TEST_PARAMS)
def test_document(line, result):
    assert _parse_single(line) == result


TXN_LINES = """
2012-12-12 * "payee" "narration"
    Assets:Cash         12.12 USD
    Assets:Cash         10 EUR @ 12 USD
    Assets:Cash         10 EUR @@ 12 USD
    Assets:Cash

2012-12-12 * "narration"
    Assets:Cash      1 * 10 USD
    Assets:Cash      100 / 10 USD
    Assets:Cash      5 + 5 USD
    Assets:Cash      15 - 5 USD
"""


def test_transaction(snapshot):
    txns = _parse_many(TXN_LINES)
    snapshot(txns)
    assert all(p.units.number == D("10") for p in txns[1].postings)
