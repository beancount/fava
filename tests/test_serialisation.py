import datetime

from beancount.core.data import (Transaction, create_simple_posting, Balance,
                                 Note)
from beancount.core.number import D
from beancount.core.amount import A
from flask.json import dumps, loads
import pytest

from fava.core.helpers import FavaAPIException
from fava.serialisation import (serialise, deserialise, extract_tags_links,
                                parse_number)


def test_parse_number():
    assert parse_number('5/2') == D('2.5')
    assert parse_number('5') == D('5')
    assert parse_number('12.345') == D('12.345')


def test_serialise(app):
    assert serialise(None) is None
    txn = Transaction({}, datetime.date(2017, 12, 12), '*', 'Test3', 'asdfasd',
                      frozenset(['tag']), frozenset(['link']), [])
    create_simple_posting(txn, 'Assets:ETrade:Cash', '100', 'USD')
    create_simple_posting(txn, 'Assets:ETrade:GLD', None, None)

    json_txn = {
        'type': 'Transaction',
        'date': '2017-12-12',
        'flag': '*',
        'payee': 'Test3',
        'narration': 'asdfasd #tag ^link',
        'meta': {},
    }

    with app.test_request_context():
        serialised = loads(dumps(serialise(txn)))

    for key, value in json_txn.items():
        assert serialised[key] == value or str(serialised[key]) == value

    assert serialised['postings'][0]['account'] == 'Assets:ETrade:Cash'
    assert serialised['postings'][0]['units'] == {
        'currency': 'USD',
        'number': 100,
    }


def test_deserialise():
    postings = [
        {
            'account': 'Assets:ETrade:Cash',
            'number': '100',
            'currency': 'USD',
        },
        {
            'account': 'Assets:ETrade:GLD',
        },
    ]
    json_txn = {
        'type': 'Transaction',
        'date': '2017-12-12',
        'flag': '*',
        'payee': 'Test3',
        'narration': 'asdfasd #tag ^link',
        'meta': {},
        'postings': postings,
    }

    txn = Transaction({}, datetime.date(2017, 12, 12), '*', 'Test3', 'asdfasd',
                      frozenset(['tag']), frozenset(['link']), [])
    create_simple_posting(txn, 'Assets:ETrade:Cash', '100', 'USD')
    create_simple_posting(txn, 'Assets:ETrade:GLD', None, None)
    assert deserialise(json_txn) == txn

    with pytest.raises(KeyError):
        deserialise({})

    with pytest.raises(FavaAPIException):
        deserialise({'type': 'NoEntry'})


def test_deserialise_balance():
    json_bal = {
        'type': 'Balance',
        'date': '2017-12-12',
        'account': 'Assets:ETrade:Cash',
        'number': '100',
        'currency': 'USD',
        'meta': {},
    }
    bal = Balance({}, datetime.date(2017, 12, 12), 'Assets:ETrade:Cash',
                  A('100 USD'), None, None)
    assert deserialise(json_bal) == bal


def test_deserialise_note():
    json_note = {
        'type': 'Note',
        'date': '2017-12-12',
        'account': 'Assets:ETrade:Cash',
        'comment': 'This is some comment or note""',
        'meta': {},
    }
    note = Note({}, datetime.date(2017, 12, 12), 'Assets:ETrade:Cash',
                'This is some comment or note')
    assert deserialise(json_note) == note


def test_extract_tags_links():
    assert extract_tags_links('notag') == ('notag', frozenset(), frozenset())
    extracted1 = ('Some text', frozenset(['tag']), frozenset())
    assert extract_tags_links('Some text #tag') == extracted1
    assert extract_tags_links('Some text ^link') == ('Some text', frozenset(),
                                                     frozenset(['link']))

    extracted2 = ('Some text', frozenset(['tag', 'tag2']), frozenset(['link']))
    assert extract_tags_links('Some text #tag #tag2 ^link') == extracted2
    assert extract_tags_links('Some text#tag#tag2 ^link') == (
        'Some text#tag#tag2', frozenset(), frozenset(['link']))
    assert extract_tags_links('Some text#tag#tag2^link') == (
        'Some text#tag#tag2^link', frozenset(), frozenset())
    assert extract_tags_links('#tag') == ('', frozenset(['tag']), frozenset())
