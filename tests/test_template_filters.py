import os.path

from beancount.core import realization
from flask import g

from fava.template_filters import (account_level, basename, get_or_create,
                                   last_segment, uptodate_eligible,
                                   should_show, should_collapse_account)


def test_basename():
    assert basename(__file__) == os.path.basename(__file__)


def test_account_level():
    assert account_level('Assets') == 1
    assert account_level('Assets:Test') == 2
    assert account_level('Assets:Test:Test') == 3


def test_last_segment():
    assert last_segment('Assets') == 'Assets'
    assert last_segment('Assets:Test') == 'Test'
    assert last_segment('Assets:Test:Test1') == 'Test1'


def test_get_or_create(example_ledger):
    assert get_or_create(example_ledger.root_account, '') == \
        example_ledger.root_account
    assert get_or_create(example_ledger.root_account, 'Expenses') == \
        realization.get(example_ledger.root_account, 'Expenses')


def test_should_show(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        assert should_show(g.ledger.root_account) is True

        assert should_show(g.ledger.root_account) is True
    with app.test_request_context('/?time=2100'):
        app.preprocess_request()
        assert not g.ledger.fava_options['show-accounts-with-zero-balance']
        assert should_show(g.ledger.root_account) is True
        empty_account = realization.get(g.ledger.root_account, 'Expenses')
        assert should_show(empty_account) is False


def test_uptodate_eligible(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        assert uptodate_eligible('Liabilities:US:Chase:Slate') is True
        assert uptodate_eligible('Liabilities:US:Chase') is False


def test_should_collapse_account(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        assert should_collapse_account('Liabilities:US:Chase:Slate') is False
        assert should_collapse_account('Liabilities:US:Chase') is False
        assert should_collapse_account('Income:US:ETrade:Dividends') is True
