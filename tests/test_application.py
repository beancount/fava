import flask
import pytest
import werkzeug.urls

from fava.application import REPORTS


FILTER_COMBINATIONS = [
    {'account': 'Assets'},
    {'from': 'has_account("Assets")'},
    {'time': '2015'},
    {'payee': 'BayBook'},
    {'tag': 'tag1, tag2'},
    {'time': '2015', 'payee': 'BayBook'},
]


@pytest.mark.parametrize('report,filters', [
    (report, filters) for report in REPORTS for filters in FILTER_COMBINATIONS
])
def test_reports(app, test_client, report, filters):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('report', report_name=report, **filters)

    result = test_client.get(url)
    assert result.status_code == 200


@pytest.mark.parametrize('query_string,result_str', [
    ('balances from year = 2014', '5086.65 USD'),
    ('nononono', 'ERROR: Syntax error near'),
    ('select sum(day)', '43558'),
])
def test_query(app, test_client, query_string, result_str):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for('query', query_string=query_string)

    result = test_client.get(url)
    assert result.status_code == 200
    assert result_str in result.get_data(True)


@pytest.mark.parametrize('url,return_code', [
    ('/', 302),
    ('/asdfasdf/', 404),
    ('/asdfasdf/asdfasdf/', 404),
])
def test_urls(app, url, return_code):
    result = app.test_client().get(url)
    assert result.status_code == return_code


@pytest.mark.parametrize('referer,jump_link,expect', [
    ('/?foo=bar', '/jump?foo=baz', '/?foo=baz'),
    ('/?foo=bar', '/jump?baz=qux', '/?baz=qux&foo=bar'),
    ('/', '/jump?foo=bar&baz=qux', '/?baz=qux&foo=bar'),
    ('/', '/jump?baz=qux', '/?baz=qux'),
    ('/?foo=bar', '/jump?foo=', '/'),
    ('/?foo=bar', '/jump?foo=&foo=', '/?foo=&foo='),
    ('/', '/jump?foo=', '/'),
])
def test_jump_handler(app, referer, jump_link, expect):
    """Test /jump handler correctly redirect to the right location.

    Note: according to RFC 2616, Location: header should use an absolute URL.
    """
    test_client = app.test_client()

    result = test_client.get(jump_link,
                             headers=[('Referer', referer)])
    with app.test_request_context():
        get_url = result.headers.get('Location', '')
        expect_url = werkzeug.urls.url_join(
            flask.url_for('root', _external=True),
            expect)
        assert result.status_code == 302
        assert get_url == expect_url
