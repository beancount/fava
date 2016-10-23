import flask


def test_api_changed(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('api_changed')

    result = test_client.get(url)
    data = flask.json.loads(result.get_data(True))
    assert data == {'changed': False, 'success': True}


def test_api_source_get(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('api_source')

    result = test_client.get(url)
    data = flask.json.loads(result.get_data(True))
    assert data == {'error': 'Trying to read a non-source file',
                    'success': False}

    path = app.config['BEANCOUNT_FILES'][0]
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('api_source', file_path=path)

    result = test_client.get(url)
    data = flask.json.loads(result.get_data(True))
    payload = open(path).read()
    assert data == {'payload': payload, 'success': True}
