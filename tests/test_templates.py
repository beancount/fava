from __future__ import annotations

from typing import TYPE_CHECKING

from flask import get_template_attribute

from fava.beans import create

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask

    from fava.core import FavaLedger


def test_render_amount(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_commodity_macros.html",
            "render_amount",
        )
        res = '<span class="num" title="US Dollar">10.00 USD</span>'
        assert macro(example_ledger, create.amount("10 USD")) == res
        res = '<span class="num"></span>'
        assert macro(example_ledger, None) == res
        res = '<span class="num" title="TEST">10.00 TEST</span>'
        assert macro(example_ledger, create.amount("10 TEST")) == res


def test_account_indicator(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html",
            "indicator",
        )
        assert not macro(example_ledger, "NONEXISTING")
        yellow_status = macro(example_ledger, "Assets:US:BofA:Checking")
        assert "yellow" in yellow_status


def test_account_name(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_account_macros.html",
            "account_name",
        )
        assert (
            macro(example_ledger, "NONEXISTING")
            == '<a href="/long-example/account/NONEXISTING/"'
            ' class="account">NONEXISTING</a>'
        )
