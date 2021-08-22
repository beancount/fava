# pylint: disable=missing-docstring
from beancount.core.amount import A

from fava.core.inventory import CounterInventory


def test_add():
    inv = CounterInventory()
    key = "KEY"
    inv.add(key, 10)
    assert len(inv) == 1
    inv.add(key, -10)
    assert inv.is_empty()


def test_add_amount():
    inv = CounterInventory()
    inv.add_amount(A("10 USD"))
    inv.add_amount(A("30 USD"))
    assert len(inv) == 1
    inv.add_amount(A("-40 USD"))
    assert inv.is_empty()

    inv.add_amount(A("10 USD"))
    inv.add_amount(A("20 CAD"))
    inv.add_amount(A("10 USD"))
    assert len(inv) == 2
    inv.add_amount(A("-20 CAD"))
    assert len(inv) == 1


def test_add_inventory():
    inv = CounterInventory()
    inv2 = CounterInventory()
    inv3 = CounterInventory()
    inv.add_amount(A("10 USD"))
    inv2.add_amount(A("30 USD"))
    inv3.add_amount(A("-40 USD"))
    inv.add_inventory(inv2)
    assert len(inv) == 1
    inv.add_inventory(inv3)
    assert inv.is_empty()
    inv = CounterInventory()
    inv.add_inventory(inv2)
    assert len(inv) == 1
