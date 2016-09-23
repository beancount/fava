import flask
import pytest
import werkzeug.urls

from fava.application import REPORTS


def test_reports(app):
    test_client = app.test_client()

    for report in REPORTS:
        with app.test_request_context():
            app.preprocess_request()
            url = flask.url_for('report', report_name=report)

        result = test_client.get(url)
        assert result.status_code == 200


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
