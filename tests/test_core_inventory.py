# pylint: disable=missing-docstring
from __future__ import annotations

from beancount.core.amount import A
from beancount.core.number import D

from fava.core.inventory import CounterInventory


def test_add() -> None:
    inv = CounterInventory()
    key = ("KEY", None)
    inv.add(key, D(10))
    assert len(inv) == 1
    inv.add(key, D(-10))
    assert inv.is_empty()


def test_add_amount() -> None:
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


def test_add_inventory() -> None:
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
