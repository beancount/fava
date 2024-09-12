from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from fava.template_filters import basename
from fava.template_filters import format_currency
from fava.template_filters import passthrough_numbers
from fava.template_filters import replace_numbers

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask


def test_incognito(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert passthrough_numbers("123123") == "123123"
        assert passthrough_numbers(None) is None
        assert replace_numbers("123123") == "XXXXXX"
        assert replace_numbers("abc123123") == "abcXXXXXX"
        assert replace_numbers(Decimal("1.1")) == "X.X"
        assert replace_numbers(None) is None


def test_format_currency(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert format_currency(Decimal("2.12")) == "2.12"


def test_basename() -> None:
    """Get the basename of a file path."""
    assert basename(__file__) == "test_template_filters.py"
