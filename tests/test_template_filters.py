from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from fava.template_filters import basename
from fava.template_filters import format_currency

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask


def test_format_currency(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert format_currency(Decimal("2.12")) == "2.12"


def test_basename() -> None:
    """Get the basename of a file path."""
    assert basename(__file__) == "test_template_filters.py"
