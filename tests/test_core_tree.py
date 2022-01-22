# pylint: disable=missing-docstring
from __future__ import annotations

from beancount.core import realization
from beancount.core.inventory import Inventory
from beancount.ops import summarize  # type: ignore[import]

from fava.core import FavaLedger
from fava.core.inventory import CounterInventory
from fava.core.tree import Tree


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


def test_tree_from_entries(example_ledger: FavaLedger) -> None:
    tree = Tree(example_ledger.entries)
    real_account = realization.realize(example_ledger.entries)

    for account in realization.iter_children(real_account):
        name = account.account
        node = tree[name]
        _compare_inv_and_counter(account.balance, node.balance)
        _compare_inv_and_counter(
            realization.compute_balance(account), node.balance_children
        )


def test_tree_cap(example_ledger: FavaLedger) -> None:
    closing_entries = summarize.cap_opt(
        example_ledger.entries, example_ledger.options
    )
    real_account = realization.realize(closing_entries)

    tree = Tree(example_ledger.entries)
    tree.cap(example_ledger.options, "Unrealized")

    for account in realization.iter_children(real_account):
        name = account.account
        node = tree[name]
        if not name:
            continue
        if name.startswith("Expenses") or name.startswith("Income"):
            continue
        _compare_inv_and_counter(account.balance, node.balance)
