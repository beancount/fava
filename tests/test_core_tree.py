from __future__ import annotations

from typing import TYPE_CHECKING

from fava.core.tree import Tree

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

    from .conftest import SnapshotFunc


def test_tree() -> None:
    tree = Tree()
    assert len(tree) == 1
    tree.get("account:name:a:b:c")
    assert len(tree) == 1
    node = tree.get("account:name:a:b:c", insert=True)
    assert tree.accounts == [
        "",
        "account",
        "account:name",
        "account:name:a",
        "account:name:a:b",
        "account:name:a:b:c",
    ]
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


def test_tree_from_entries(
    example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    tree = Tree(example_ledger.all_entries)

    snapshot({n.name: n.balance.to_strings() for n in tree.values()})
    snapshot(tree["Assets"].balance_children.to_strings())


def test_tree_cap(example_ledger: FavaLedger, snapshot: SnapshotFunc) -> None:
    tree = Tree(example_ledger.all_entries)
    tree.cap(example_ledger.options, "Unrealized")

    snapshot({n.name: n.balance.to_strings() for n in tree.values()})
