# pylint: disable=missing-docstring
from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

import pytest
from beancount.core import realization
from beancount.core.number import D
from flask import Flask
from pytest import MonkeyPatch

from fava.context import g
from fava.core import FavaLedger
from fava.core.accounts import AccountData
from fava.core.inventory import CounterInventory
from fava.core.tree import TreeNode
from fava.template_filters import basename
from fava.template_filters import collapse_account
from fava.template_filters import format_currency
from fava.template_filters import format_date
from fava.template_filters import format_errormsg
from fava.template_filters import get_or_create
from fava.template_filters import remove_keys
from fava.template_filters import should_show


def test_remove_keys() -> None:
    """Dict keys get remove or return empty dict if None is given."""
    assert not remove_keys(None, [])
    assert not remove_keys({"asdf": 1}, ["asdf"])


@pytest.mark.parametrize(
    "interval,output",
    [
        ("year", "2012"),
        ("quarter", "2012Q4"),
        ("month", "Dec 2012"),
        ("week", "2012W51"),
        ("day", "2012-12-20"),
    ],
)
def test_format_date(app: Flask, interval: str, output: str) -> None:
    test_date = date(2012, 12, 20)
    url = (
        f"/long-example/?interval={interval}" if interval else "/long-example"
    )
    with app.test_request_context(url):
        app.preprocess_request()
        assert format_date(test_date) == output


def test_format_currency(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert format_currency(Decimal("2.12")) == "2.12"
        assert format_currency(Decimal("2.13"), invert=True) == "-2.13"


def test_basename() -> None:
    """Get the basename of a file path."""
    assert basename(__file__) == "test_template_filters.py"


def test_get_or_create(example_ledger: FavaLedger) -> None:
    assert (
        get_or_create(example_ledger.root_account, "")
        == example_ledger.root_account
    )
    assert get_or_create(
        example_ledger.root_account, "Expenses"
    ) == realization.get(example_ledger.root_account, "Expenses")


def test_should_show(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert should_show(g.ledger.root_tree.get("")) is True
        assert should_show(g.ledger.root_tree.get("Expenses")) is True

        account = TreeNode("name")
        assert should_show(account) is False
        account.balance_children = CounterInventory({("USD", None): D("9")})
        assert should_show(account) is True
    with app.test_request_context("/long-example/income_statement/?time=2100"):
        app.preprocess_request()
        assert not g.ledger.fava_options.show_accounts_with_zero_balance
        assert should_show(g.ledger.root_tree.get("")) is True
        assert should_show(g.ledger.root_tree.get("Expenses")) is False


def test_format_errormsg(app: Flask) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        assert (
            format_errormsg("Test for 'Expenses:Acme:Cash': Test")
            == 'Test for <a href="/long-example/account/Expenses:'
            'Acme:Cash/">Expenses:Acme:Cash</a>: Test'
        )
        assert (
            format_errormsg("Test Expenses:Acme:Cash Test")
            == 'Test <a href="/long-example/account/Expenses:'
            'Acme:Cash/">Expenses:Acme:Cash</a> Test'
        )
        assert format_errormsg("Test: Test") == "Test: Test"


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
