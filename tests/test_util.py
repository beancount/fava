from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from babel import Locale
from werkzeug.exceptions import NotFound
from werkzeug.test import Client
from werkzeug.wrappers import Response

from fava.util import get_translations
from fava.util import listify
from fava.util import next_key
from fava.util import send_file_inline
from fava.util import simple_wsgi
from fava.util import slugify

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from pathlib import Path

    from flask import Flask


def test_get_translations() -> None:
    de = get_translations(Locale.parse("de"))
    assert de
    assert de == get_translations(Locale.parse("de_AT"))
    assert get_translations(Locale.parse("pt"))
    pt = get_translations(Locale.parse("pt_PT"))
    assert pt
    assert "pt" in pt
    assert "pt_BR" not in pt
    assert get_translations(Locale.parse("pt_BR"))

    zh = get_translations(Locale.parse("zh"))
    assert zh
    assert "zh" in zh
    assert "zh_Hant_TW" not in zh
    zh_tw = get_translations(Locale.parse("zh_TW"))
    assert zh_tw
    assert "zh_Hant_TW" in zh_tw

    assert not get_translations(Locale.parse("km"))


def test_listify() -> None:
    @listify
    def fun() -> Iterable[int]:
        yield from [1, 2, 3]

    assert fun() == [1, 2, 3]


def test_simple_wsgi() -> None:
    client = Client(simple_wsgi, Response)
    response = client.get("/any_path")
    assert response.status_code == HTTPStatus.OK.value
    assert response.data == b""


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
        assert (
            resp.headers["Content-Disposition"]
            == "inline; filename*=UTF-8''example-utf8-%F0%9F%A6%81.txt"
        )
        with pytest.raises(NotFound):
            resp = send_file_inline(str(test_data_dir / "non-existent-file"))
