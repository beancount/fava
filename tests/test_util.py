# pylint: disable=missing-docstring

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from fava.util import simple_wsgi, slugify, pairwise, listify, send_file_inline

from .conftest import data_file


def test_listify():
    @listify
    def fun():
        for i in [1, 2, 3]:
            yield i

    assert fun() == [1, 2, 3]


def test_pairwise():
    assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3)]
    assert list(pairwise([])) == []


def test_simple_wsgi():
    client = Client(simple_wsgi, BaseResponse)
    resp = client.get("/any_path")
    assert resp.status_code == 200
    assert resp.data == b""


def test_slugify():
    assert slugify("Example Beancount File") == "example-beancount-file"
    assert slugify("    Example Beancount File  ") == "example-beancount-file"
    assert slugify("test") == "test"
    assert slugify("烫烫烫") == "烫烫烫"
    assert slugify("nonun烫icode 烫烫") == "nonun烫icode-烫烫"
    assert slugify("%✓") == ""
    assert slugify("söße") == "söße"
    assert slugify("ASDF") == "asdf"
    assert slugify("ASDF test test") == "asdf-test-test"


def test_send_file_inline(app):
    with app.test_request_context():
        app.preprocess_request()
        resp = send_file_inline(data_file("example-balances.csv"))
        assert (
            resp.headers["Content-Disposition"]
            == "inline; filename*=UTF-8''example-balances.csv"
        )
        resp = send_file_inline(data_file("example-utf8-🦁.txt"))
        # pylint: disable=line-too-long
        assert (
            resp.headers["Content-Disposition"]
            == "inline; filename*=UTF-8''example-utf8-%F0%9F%A6%81.txt"
        )
