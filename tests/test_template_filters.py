# pylint: disable=missing-docstring

import os.path

from flask import g
from beancount.core import realization

from fava.core import AccountData
from fava.core.inventory import CounterInventory
from fava.core.tree import TreeNode
from fava.template_filters import (
    basename,
    get_or_create,
    should_show,
    format_errormsg,
    collapse_account,
)


def test_basename():
    assert basename(__file__) == os.path.basename(__file__)


def test_get_or_create(example_ledger):
    assert (
        get_or_create(example_ledger.root_account, "")
        == example_ledger.root_account
    )
    assert get_or_create(
        example_ledger.root_account, "Expenses"
    ) == realization.get(example_ledger.root_account, "Expenses")


def test_should_show(app):
    with app.test_request_context("/"):
        app.preprocess_request()
        assert should_show(g.ledger.root_tree.get("")) is True
        assert should_show(g.ledger.root_tree.get("Expenses")) is True

        account = TreeNode("name")
        assert should_show(account) is False
        account.balance_children = CounterInventory({("USD", None): 9})
        assert should_show(account) is True
    with app.test_request_context("/?time=2100"):
        app.preprocess_request()
        assert not g.ledger.fava_options["show-accounts-with-zero-balance"]
        assert should_show(g.ledger.root_tree.get("")) is True
        assert should_show(g.ledger.root_tree.get("Expenses")) is False


def test_format_errormsg(app):
    with app.test_request_context("/"):
        app.preprocess_request()
        assert (
            format_errormsg("Test for 'Expenses:Acme:Cash': Test")
            == 'Test for <a href="/example-beancount-file/account/Expenses:'
            'Acme:Cash/">Expenses:Acme:Cash</a>: Test'
        )
        assert (
            format_errormsg("Test Expenses:Acme:Cash Test")
            == 'Test <a href="/example-beancount-file/account/Expenses:'
            'Acme:Cash/">Expenses:Acme:Cash</a> Test'
        )
        assert format_errormsg("Test: Test") == "Test: Test"


def test_collapse_account(app):
    with app.test_request_context("/"):
        app.preprocess_request()
        g.ledger.fava_options["collapse-pattern"] = [
            "^Assets:Stock$",
            "^Assets:Property:.*",
        ]
        g.ledger.accounts["Assets:Stock"] = AccountData()
        g.ledger.accounts["Assets:Property"] = AccountData()

        assert collapse_account("Assets:Cash") is False
        assert collapse_account("Assets:Cash") is False

        assert collapse_account("Assets:Stock") is True
        assert collapse_account("Assets:Stock") is True
        assert collapse_account("Assets:Stock") is True

        assert collapse_account("Assets:Property") is False
        assert collapse_account("Assets:Property:Real") is True
        assert collapse_account("Assets:Property:Real:Land") is True
