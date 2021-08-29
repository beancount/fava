# pylint: disable=missing-docstring
from werkzeug.test import Client
from werkzeug.wrappers import Response

from .conftest import data_file
from fava.util import listify
from fava.util import next_key
from fava.util import pairwise
from fava.util import send_file_inline
from fava.util import simple_wsgi
from fava.util import slugify


def test_listify():
    @listify
    def fun():
        yield from [1, 2, 3]

    assert fun() == [1, 2, 3]


def test_pairwise():
    assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3)]
    assert list(pairwise([])) == []


def test_simple_wsgi():
    client = Client(simple_wsgi, Response)
    resp = client.get("/any_path")
    assert resp.status_code == 200
    assert resp.data == b""


def test_next_key() -> None:
    assert next_key("statement", {}) == "statement"
    assert next_key("statement", {"foo": 1}) == "statement"
    assert next_key("statement", {"foo": 1, "statement": 1}) == "statement-2"
    assert (
        next_key("statement", {"statement": 1, "statement-2": 1})
        == "statement-3"
    )


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
