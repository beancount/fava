from io import BytesIO
import os

from beancount.scripts.format import align_beancount
import flask


def test_api_changed(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.changed')

    result = test_client.get(url)
    data = flask.json.loads(result.get_data(True))
    assert data == {'changed': False, 'success': True}


def test_api_add_document(app, test_client, tmpdir):
    with app.test_request_context():
        app.preprocess_request()
        old_documents = flask.g.ledger.options['documents']
        flask.g.ledger.options['documents'] = [str(tmpdir)]
        data = {
            'folder': str(tmpdir),
            'account': 'Test',
            'filename': '2015-12-12_test',
            'file': (BytesIO(b'asdfasdf'), 'test'),
        }
        url = flask.url_for('json_api.add_document')

        response = test_client.put(url)
        assert response.status_code == 400

        filename = '{}/{}/{}'.format(
            str(tmpdir), 'Test', data['filename'].replace('_', ' '))

        response = test_client.put(url, data=data)
        assert flask.json.loads(response.get_data(True)) == {
            'success': True,
            'message': 'Uploaded to {}'.format(filename),
        }
        assert os.path.isfile(filename)

        data['file'] = (BytesIO(b'asdfasdf'), 'test')
        response = test_client.put(url, data=data)
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
    data = flask.json.loads(result.get_data(True))
    assert data == {'error': 'Trying to read a non-source file',
                    'success': False}

    path = app.config['BEANCOUNT_FILES'][0]
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.source', file_path=path)

    result = test_client.get(url)
    data = flask.json.loads(result.get_data(True))
    payload = open(path).read()
    assert data == {'payload': payload, 'success': True}


def test_api_source_put(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('json_api.source')

    # test bad request
    response = test_client.put(url)
    assert response.status_code == 400

    path = app.config['BEANCOUNT_FILES'][0]
    payload = open(path).read()

    # change source
    result = test_client.put(url, data=flask.json.dumps({
        'source': 'asdf' + payload,
        'file_path': path,
    }), content_type='application/json')
    assert result.status_code == 200
    data = flask.json.loads(result.get_data(True))
    assert data == {'success': True}

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

    # test bad request
    response = test_client.post(url)
    assert response.status_code == 400
