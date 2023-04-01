# pylint: disable=missing-docstring
from __future__ import annotations

from beancount.core.inventory import Inventory

from fava.core import FavaLedger
from fava.core.inventory import CounterInventory
from fava.core.tree import Tree

from .conftest import SnapshotFunc


def test_tree() -> None:
    tree = Tree()
    assert len(tree) == 1
    tree.get("account:name:a:b:c")
    assert len(tree) == 1
    node = tree.get("account:name:a:b:c", insert=True)
    assert len(tree) == 6
    tree.get("account:name", insert=True)
    assert len(tree) == 6
    assert node is tree.get("account:name:a:b:c", insert=True)

    assert list(tree.ancestors("account:name:a:b:c")) == [
        tree.get("account:name:a:b"),
        tree.get("account:name:a"),
        tree.get("account:name"),
        tree.get("account"),
        tree.get(""),
    ]

    assert len(list(tree.ancestors("not:account:name:a:b:c"))) == 6


def _compare_inv_and_counter(
    inv: Inventory | None, counter: CounterInventory
) -> None:
    assert inv is not None
    for pos in inv:
        assert pos.units.number == counter[(pos.units.currency, pos.cost)]
    if counter:
        assert len(inv) == len(counter)


def test_tree_from_entries(
    example_ledger: FavaLedger, snapshot: SnapshotFunc
) -> None:
    tree = Tree(example_ledger.all_entries)

    snapshot({n.name: n.balance for n in tree.values()})
    snapshot(tree["Assets"].balance_children)


def test_tree_cap(example_ledger: FavaLedger, snapshot: SnapshotFunc) -> None:
    tree = Tree(example_ledger.all_entries)
    tree.cap(example_ledger.options, "Unrealized")

    snapshot({n.name: n.balance for n in tree.values()})
