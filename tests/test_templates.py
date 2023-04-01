# pylint: disable=missing-docstring
from __future__ import annotations

import re
from decimal import Decimal

from flask import Flask
from flask import get_template_attribute

from fava.beans import create
from fava.context import g
from fava.core import FavaLedger
from fava.core.inventory import CounterInventory

from .conftest import SnapshotFunc

A = create.amount

COMMODITY_MACROS_PATH = "macros/_commodity_macros.html"
TREE_TABLE_PATH = "_tree_table.html"


def test_render_diff_and_number(app: Flask, snapshot: SnapshotFunc) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            TREE_TABLE_PATH, "render_diff_and_number"
        )

        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(12)})
            cost = CounterInventory({"EUR": Decimal(10)})
            snapshot(macro(balance, cost, "EUR", invert))
        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(10)})
            cost = CounterInventory({"EUR": Decimal(12)})
            snapshot(macro(balance, cost, "EUR", invert))


def test_account_tree(app: Flask, snapshot: SnapshotFunc) -> None:
    with app.test_request_context("/long-example/?time=2015"):
        app.preprocess_request()

        macro = get_template_attribute(TREE_TABLE_PATH, "account_tree")
        interval_balances, interval_ends = g.ledger.interval_balances(
            g.filtered, g.interval, "Assets"
        )
        snapshot(
            re.sub(
                r"\d+ days ago",
                "X days ago",
                macro(
                    "Assets",
                    interval_balances,
                    interval_ends,
                    False,
                    ledger=g.ledger,
                ),
            )
        )


def test_render_currency(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            COMMODITY_MACROS_PATH, "render_currency"
        )
        assert "US Dollar" in macro(example_ledger, "USD")
        test = '<span title="TEST">TEST</span>'
        assert macro(example_ledger, "TEST") == test


def test_render_amount(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(COMMODITY_MACROS_PATH, "render_amount")
        res = '<span class="num" title="US Dollar">10.00 USD</span>'
        assert macro(example_ledger, A("10 USD")) == res
        res = '<span class="num"></span>'
        assert macro(example_ledger, None) == res
        res = '<span class="num" title="TEST">10.00 TEST</span>'
        assert macro(example_ledger, A("10 TEST")) == res


def test_account_indicator(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html", "indicator"
        )
        assert not macro(example_ledger, "NONEXISTING")
        yellow_status = macro(example_ledger, "Assets:US:BofA:Checking")
        assert "yellow" in yellow_status


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