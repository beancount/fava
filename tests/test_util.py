# pylint: disable=missing-docstring
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response

from fava.util import listify
from fava.util import next_key
from fava.util import pairwise
from fava.util import send_file_inline
from fava.util import simple_wsgi
from fava.util import slugify


def test_listify() -> None:
    @listify
    def fun() -> Iterable[int]:
        yield from [1, 2, 3]

    assert fun() == [1, 2, 3]


def test_pairwise() -> None:
    assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3)]
    assert not list(pairwise([]))


def test_simple_wsgi() -> None:
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


def test_slugify() -> None:
    assert slugify("Example Beancount File") == "example-beancount-file"
    assert slugify("    Example Beancount File  ") == "example-beancount-file"
    assert slugify("test") == "test"
    assert slugify("烫烫烫") == "烫烫烫"
    assert slugify("nonun烫icode 烫烫") == "nonun烫icode-烫烫"
    assert not slugify("%✓")
    assert slugify("söße") == "söße"
    assert slugify("ASDF") == "asdf"
    assert slugify("ASDF test test") == "asdf-test-test"


def test_send_file_inline(app: Flask, test_data_dir: Path) -> None:
    with app.test_request_context():
        resp = send_file_inline(str(test_data_dir / "example-balances.csv"))
        assert (
            resp.headers["Content-Disposition"]
            == "inline; filename*=UTF-8''example-balances.csv"
        )
        resp = send_file_inline(str(test_data_dir / "example-utf8-🦁.txt"))
        # pylint: disable=line-too-long
        assert (
            resp.headers["Content-Disposition"]
            == "inline; filename*=UTF-8''example-utf8-%F0%9F%A6%81.txt"
        )
