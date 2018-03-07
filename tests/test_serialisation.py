import datetime

from beancount.core.data import Transaction, create_simple_posting
from beancount.core.number import D
import pytest

from fava.core.helpers import FavaAPIException
from fava.serialisation import deserialise, extract_tags_links, parse_number


def test_parse_number():
    assert parse_number('5/2') == D('2.5')
    assert parse_number('5') == D('5')
    assert parse_number('12.345') == D('12.345')


def test_deserialise():
    json_txn = {
        'type': 'Transaction',
        'date': '2017-12-12',
        'flag': '*',
        'payee': 'Test3',
        'narration': 'asdfasd #tag ^link',
        'meta': {},
        'postings': [
            {
                'account': 'Assets:ETrade:Cash',
                'number': '100',
                'currency': 'USD',
            },
            {
                'account': 'Assets:ETrade:GLD',
            },
        ],
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


def test_extract_tags_links():
    assert extract_tags_links('notag') == ('notag', frozenset(), frozenset())
    assert extract_tags_links('Some text #tag') == (
        'Some text', frozenset(['tag']), frozenset())
    assert extract_tags_links('Some text ^link') == ('Some text', frozenset(),
                                                     frozenset(['link']))
    assert extract_tags_links('Some text #tag #tag2 ^link') == (
        'Some text', frozenset(['tag', 'tag2']), frozenset(['link']))
    assert extract_tags_links('Some text#tag#tag2 ^link') == (
        'Some text#tag#tag2', frozenset(), frozenset(['link']))
    assert extract_tags_links('Some text#tag#tag2^link') == (
        'Some text#tag#tag2^link', frozenset(), frozenset())
    assert extract_tags_links('#tag') == ('', frozenset(['tag']), frozenset())
