# pylint: disable=missing-docstring
from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

import pytest
from flask import Flask
from pytest import MonkeyPatch

from fava.beans import create
from fava.context import g
from fava.core.accounts import AccountData
from fava.core.inventory import CounterInventory
from fava.core.tree import TreeNode
from fava.template_filters import basename
from fava.template_filters import collapse_account
from fava.template_filters import format_currency
from fava.template_filters import format_date
from fava.template_filters import format_date_filter
from fava.template_filters import remove_keys
from fava.template_filters import should_show

D = create.decimal


def test_remove_keys() -> None:
    """Dict keys get remove or return empty dict if None is given."""
    assert not remove_keys(None, [])
    assert not remove_keys({"asdf": 1}, ["asdf"])


@pytest.mark.parametrize(
    "interval,output,output_filter",
    [
        ("year", "2012", "2012"),
        ("quarter", "2012Q4", "2012-Q4"),
        ("month", "Dec 2012", "2012-12"),
        ("week", "2012W51", "2012-W51"),
        ("day", "2012-12-20", "2012-12-20"),
    ],
)
def test_format_date(
    app: Flask, interval: str, output: str, output_filter: str
) -> None:
    test_date = date(2012, 12, 20)
    url = (
        f"/long-example/?interval={interval}" if interval else "/long-example"
    )
    with app.test_request_context(url):
        app.preprocess_request()
        assert format_date(test_date) == output
        assert format_date_filter(test_date) == output_filter


def test_format_currency(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert format_currency(Decimal("2.12")) == "2.12"
        assert format_currency(Decimal("2.13"), invert=True) == "-2.13"


def test_basename() -> None:
    """Get the basename of a file path."""
    assert basename(__file__) == "test_template_filters.py"


def test_should_show(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert should_show(g.filtered.root_tree.get("")) is True
        assert should_show(g.filtered.root_tree.get("Expenses")) is True

        account = TreeNode("name")
        assert should_show(account) is False
        account.balance_children = CounterInventory({("USD", None): D("9")})
        assert should_show(account) is True
    with app.test_request_context("/long-example/income_statement/?time=2100"):
        app.preprocess_request()
        assert not g.ledger.fava_options.show_accounts_with_zero_balance
        assert should_show(g.filtered.root_tree.get("")) is True
        assert should_show(g.filtered.root_tree.get("Expenses")) is False


def test_collapse_account(app: Flask, monkeypatch: MonkeyPatch) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setattr(
            g.ledger.fava_options,
            "collapse_pattern",
            [
                re.compile("^Assets:Stock$"),
                re.compile("^Assets:Property:.*"),
            ],
        )
        monkeypatch.setitem(g.ledger.accounts, "Assets:Stock", AccountData())
        monkeypatch.setitem(
            g.ledger.accounts, "Assets:Property", AccountData()
        )

        assert collapse_account("Assets:Cash") is False
        assert collapse_account("Assets:Cash") is False

        assert collapse_account("Assets:Stock") is True
        assert collapse_account("Assets:Stock") is True
        assert collapse_account("Assets:Stock") is True

        assert collapse_account("Assets:Property") is False
        assert collapse_account("Assets:Property:Real") is True
        assert collapse_account("Assets:Property:Real:Land") is True
