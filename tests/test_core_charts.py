from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from fava.util.date import Interval

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


def test_interval_totals(
    small_example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    filtered = small_example_ledger.get_filtered()
    for conversion in ["at_cost", "USD"]:
        data = small_example_ledger.charts.interval_totals(
            filtered,
            Interval.MONTH,
            "Expenses",
            conversion,
        )
        snapshot(data, json=True)


def test_interval_totals_inverted(
    small_example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    filtered = small_example_ledger.get_filtered()
    for conversion in ["at_cost", "USD"]:
        data = small_example_ledger.charts.interval_totals(
            filtered,
            Interval.MONTH,
            "Expenses",
            conversion,
            invert=True,
        )
        snapshot(data, json=True)


def test_linechart_data(
    example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    filtered = example_ledger.get_filtered()
    for conversion in ["at_cost", "units", "at_value", "USD"]:
        data = example_ledger.charts.linechart(
            filtered,
            "Assets:Testing:MultipleCommodities",
            conversion,
        )
        snapshot(data, json=True)

    assert not example_ledger.charts.linechart(
        filtered,
        "Assets:Testing:MultipleCommodities:NotAnAccount",
        "units",
    )


def test_net_worth(example_ledger: FavaLedger, snapshot: SnapshotFunc) -> None:
    filtered = example_ledger.get_filtered()
    data = example_ledger.charts.net_worth(filtered, Interval.MONTH, "USD")
    snapshot(data, json=True)


def test_net_worth_off_by_one(
    snapshot: SnapshotFunc,
    get_ledger: GetFavaLedger,
) -> None:
    off_by_one = get_ledger("off-by-one")
    off_by_one_filtered = off_by_one.get_filtered()
    assert not off_by_one.errors
    assert len(off_by_one_filtered.entries) == 9

    for interval in [Interval.DAY, Interval.MONTH]:
        data = off_by_one.charts.net_worth(
            off_by_one_filtered,
            interval,
            "at_value",
        )
        assert len(data) == 4 if interval == Interval.DAY else 1
        snapshot(data, json=True)


def test_hierarchy(example_ledger: FavaLedger) -> None:
    filtered = example_ledger.get_filtered()
    data = example_ledger.charts.hierarchy(filtered, "Assets", "at_cost")
    assert data.balance_children == {
        "IRAUSD": Decimal("7200.00"),
        "USD": Decimal("94320.27840"),
        "VACHR": Decimal(-82),
    }
    assert data.balance == {}
    etrade = data.children[1].children[2]
    assert etrade.account == "Assets:US:ETrade"
    assert etrade.balance_children == {"USD": Decimal("23137.54")}
