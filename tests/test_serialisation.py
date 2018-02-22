import datetime

from beancount.core.data import Transaction, create_simple_posting

from fava.serialisation import deserialise, extract_tags_links


def test_deserialise():
    valid_accounts = ['Assets:ETrade:Cash', 'Assets:ETrade:GLD']
    json_txn = {
        'type': 'Transaction',
        'date': '2017-12-12',
        'flag': '*',
        'payee': 'Test3',
        'narration': 'asdfasd',
        'metadata': {},
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
                      frozenset(), frozenset(), [])
    create_simple_posting(txn, 'Assets:ETrade:Cash', '100', 'USD')
    create_simple_posting(txn, 'Assets:ETrade:GLD', None, None)
    assert deserialise(json_txn, valid_accounts) == txn


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
