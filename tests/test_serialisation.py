import datetime

from beancount.core.data import Transaction, create_simple_posting

from fava.serialisation import deserialise


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
