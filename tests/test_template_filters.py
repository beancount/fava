import os.path

from beancount.core import realization
from flask import g

from fava.core.inventory import CounterInventory
from fava.core.tree import TreeNode
from fava.template_filters import basename, get_or_create, should_show


def test_basename():
    assert basename(__file__) == os.path.basename(__file__)


def test_get_or_create(example_ledger):
    assert get_or_create(example_ledger.root_account, '') == \
        example_ledger.root_account
    assert get_or_create(example_ledger.root_account, 'Expenses') == \
        realization.get(example_ledger.root_account, 'Expenses')


def test_should_show(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        assert should_show(g.ledger.root_tree.get('')) is True
        assert should_show(g.ledger.root_tree.get('Expenses')) is True

        account = TreeNode('name')
        assert should_show(account) is False
        account.balance_children = CounterInventory({('USD', None): 9})
        assert should_show(account) is True
    with app.test_request_context('/?time=2100'):
        app.preprocess_request()
        assert not g.ledger.fava_options['show-accounts-with-zero-balance']
        assert should_show(g.ledger.root_tree.get('')) is True
        assert should_show(g.ledger.root_tree.get('Expenses')) is False
