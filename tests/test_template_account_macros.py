# pylint: disable=missing-docstring
from __future__ import annotations

import datetime

from flask import Flask
from flask import get_template_attribute

from fava.core import FavaLedger


def test_indicator(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html", "indicator"
        )
        assert macro(example_ledger, "NONEXISTING") == ""
        yellow_status = macro(example_ledger, "Assets:US:BofA:Checking")
        assert "yellow" in yellow_status


def test_balance_directive(app: Flask, example_ledger: FavaLedger) -> None:
    today = datetime.date.today()
    bal = f"{today} balance Assets:US:BofA:Checking              1632.79 USD\n"
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html", "balance_directive"
        )
        assert macro(example_ledger, "NONEXISTING") == ""
        assert macro(example_ledger, "Assets:US:BofA:Checking") == f"{bal}"


def test_account_name(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_account_macros.html", "account_name"
        )
        assert (
            macro(example_ledger, "NONEXISTING")
            == '<a href="/long-example/account/NONEXISTING/"'
            ' class="account">NONEXISTING</a>\n'
        )
        assert (
            macro(example_ledger, "Assets:US:BofA:Checking")
            == '<a href="/long-example/account/Assets:US:BofA:Checking/"'
            ' class="account">Assets:US:BofA:Checking</a>\n'
        )
