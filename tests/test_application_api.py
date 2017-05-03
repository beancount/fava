import datetime
from io import BytesIO
import os

from beancount.core.data import Transaction, create_simple_posting
from beancount.scripts.format import align_beancount
import flask

from fava.json_api import json_to_entry


def test_api_changed(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.changed')

    result = test_client.get(url)
    response_data = flask.json.loads(result.get_data(True))
    assert response_data == {'changed': False, 'success': True}


def test_api_add_document(app, test_client, tmpdir):
    with app.test_request_context():
        app.preprocess_request()
        old_documents = flask.g.ledger.options['documents']
        flask.g.ledger.options['documents'] = [str(tmpdir)]
        request_data = {
            'folder': str(tmpdir),
            'account': 'Test',
            'filename': '2015-12-12_test',
            'file': (BytesIO(b'asdfasdf'), 'test'),
        }
        url = flask.url_for('json_api.add_document')

        response = test_client.put(url)
        assert response.status_code == 400

        filename = '{}/{}/{}'.format(
            str(tmpdir), 'Test', request_data['filename'].replace('_', ' '))

        response = test_client.put(url, data=request_data)
        assert flask.json.loads(response.get_data(True)) == {
            'success': True,
            'message': 'Uploaded to {}'.format(filename),
        }
        assert os.path.isfile(filename)

        request_data['file'] = (BytesIO(b'asdfasdf'), 'test')
        response = test_client.put(url, data=request_data)
        assert flask.json.loads(response.get_data(True)) == {
            'success': False,
            'error': '{} already exists.'.format(filename),
        }
        flask.g.ledger.options['documents'] = old_documents


def test_api_source_get(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.source')

    result = test_client.get(url)
    response_data = flask.json.loads(result.get_data(True))
    assert response_data == {
        'error': 'Trying to read a non-source file',
        'success': False
    }

    path = app.config['BEANCOUNT_FILES'][0]
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.source', file_path=path)

    result = test_client.get(url)
    response_data = flask.json.loads(result.get_data(True))
    payload = open(path).read()
    assert response_data == {'payload': payload, 'success': True}


def test_api_source_put(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.source')

    # test bad request
    response = test_client.put(url)
    response_data = flask.json.loads(response.get_data(True))
    assert response_data == {
        'error': 'Invalid JSON request.',
        'success': False
    }
    assert response.status_code == 200

    path = app.config['BEANCOUNT_FILES'][0]
    payload = open(path).read()

    # change source
    result = test_client.put(url, data=flask.json.dumps({
        'source': 'asdf' + payload,
        'file_path': path,
    }), content_type='application/json')
    assert result.status_code == 200
    response_data = flask.json.loads(result.get_data(True))
    assert response_data == {'success': True}

    # check if the file has been written
    assert open(path).read() == 'asdf' + payload

    # write original source file
    result = test_client.put(url, data=flask.json.dumps({
        'source': payload,
        'file_path': path,
    }), content_type='application/json')
    assert result.status_code == 200
    assert open(path).read() == payload


def test_api_format_source(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.format_source')

    path = app.config['BEANCOUNT_FILES'][0]
    payload = open(path).read()

    result = test_client.post(url, data=flask.json.dumps({'source': payload}),
                              content_type='application/json')
    data = flask.json.loads(result.get_data(True))
    assert data == {'payload': align_beancount(payload),
                    'success': True}


def test_json_to_entry():
    valid_accounts = ['Assets:US:ETrade:Cash', 'Assets:US:ETrade:GLD']
    json_txn = {
        'type': 'transaction',
        'date': '2017-12-12',
        'flag': '*',
        'payee': 'Test3',
        'narration': '',
        'metadata': {},
        'postings': [
            {
                'account': 'Assets:US:ETrade:Cash',
                'number': '100',
                'currency': 'USD',
            },
            {
                'account': 'Assets:US:ETrade:GLD',
            },
        ],
    }

    txn = Transaction({}, datetime.date(2017, 12, 12), '*', 'Test3', '',
                      frozenset(), frozenset(), [])
    create_simple_posting(txn, 'Assets:US:ETrade:Cash', '100', 'USD')
    create_simple_posting(txn, 'Assets:US:ETrade:GLD', None, None)
    assert json_to_entry(json_txn, valid_accounts) == txn


def test_api_add_entries(app, test_client, tmpdir):
    with app.test_request_context():
        app.preprocess_request()
        old_beancount_file = flask.g.ledger.beancount_file_path
        test_file = tmpdir.join('test_file')
        test_file.open('a')
        flask.g.ledger.beancount_file_path = str(test_file)

        data = {
            'entries': [
                {
                    'type': 'transaction',
                    'date': '2017-12-12',
                    'flag': '*',
                    'payee': 'Test3',
                    'narration': '',
                    'metadata': {},
                    'postings': [
                        {
                            'account': 'Assets:US:ETrade:Cash',
                            'number': '100',
                            'currency': 'USD',
                        },
                        {
                            'account': 'Assets:US:ETrade:GLD',
                        },
                    ],
                },
                {
                    'type': 'transaction',
                    'date': '2017-01-12',
                    'flag': '*',
                    'payee': 'Test1',
                    'narration': '',
                    'metadata': {},
                    'postings': [
                        {
                            'account': 'Assets:US:ETrade:Cash',
                            'number': '100',
                            'currency': 'USD',
                        },
                        {
                            'account': 'Assets:US:ETrade:GLD',
                        },
                    ],
                },
                {
                    'type': 'transaction',
                    'date': '2017-02-12',
                    'flag': '*',
                    'payee': 'Test',
                    'narration': 'Test',
                    'metadata': {},
                    'postings': [
                        {
                            'account': 'Assets:US:ETrade:Cash',
                            'number': '100',
                            'currency': 'USD',
                        },
                        {
                            'account': 'Assets:US:ETrade:GLD',
                        },
                    ],
                },
            ]
        }
        url = flask.url_for('json_api.add_entries')

        response = test_client.put(url, data=flask.json.dumps(data),
                                   content_type='application/json')
        assert flask.json.loads(response.get_data(True)) == {
            'success': True,
            'message': 'Stored 3 entries.',
        }

        assert test_file.read_text('utf-8') == """2017-01-12 * "Test1" ""
  Assets:US:ETrade:Cash  100 USD
  Assets:US:ETrade:GLD

2017-02-12 * "Test" "Test"
  Assets:US:ETrade:Cash  100 USD
  Assets:US:ETrade:GLD

2017-12-12 * "Test3" ""
  Assets:US:ETrade:Cash  100 USD
  Assets:US:ETrade:GLD

"""

        flask.g.ledger.beancount_file_path = old_beancount_file
