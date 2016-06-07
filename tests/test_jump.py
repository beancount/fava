"""This file contains test for the /jump handler."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import flask
import pytest
import werkzeug.urls


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
        assert result.status_code == 302 and get_url == expect_url
