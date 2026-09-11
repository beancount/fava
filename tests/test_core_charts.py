from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import TYPE_CHECKING

from fava.core import FavaLedger
from fava.core.conversion import AT_COST
from fava.util.date import Day
from fava.util.date import Month

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

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
            Month,
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
            Month,
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
    data = example_ledger.charts.net_worth(filtered, Month, "USD")
    snapshot(data, json=True)


def test_net_worth_off_by_one(
    snapshot: SnapshotFunc,
    get_ledger: GetFavaLedger,
) -> None:
    off_by_one = get_ledger("off-by-one")
    off_by_one_filtered = off_by_one.get_filtered()
    assert not off_by_one.errors
    assert len(off_by_one_filtered.entries) == 9

    for interval in [Day, Month]:
        data = off_by_one.charts.net_worth(
            off_by_one_filtered,
            interval,
            "at_value",
        )
        assert len(data) == 4 if interval == Day else 1
        snapshot(data, json=True)


def test_hierarchy(example_ledger: FavaLedger) -> None:
    filtered = example_ledger.get_filtered()

    data = example_ledger.charts.hierarchy(filtered, "Assets", AT_COST)
    assert data.balance_children == {
        "IRAUSD": Decimal("7200.00"),
        "USD": Decimal("94320.27840"),
        "VACHR": Decimal(-82),
    }
    assert data.balance == {}
    etrade = data.children[1].children[2]
    assert etrade.account == "Assets:US:ETrade"
    assert etrade.balance_children == {"USD": Decimal("23137.54")}


def test_interval_totals_sibling_with_shared_prefix(tmp_path: Path) -> None:
    """Accounts that merely share a name prefix are not children."""
    ledger_path = tmp_path / "prefix.beancount"
    ledger_path.write_text(
        dedent("""\
            option "operating_currency" "USD"

            2016-01-01 open Assets:Cash
            2016-01-01 open Expenses:Car
            2016-01-01 open Expenses:Car:Fuel
            2016-01-01 open Expenses:Carpet

            2016-01-05 * "fuel"
              Expenses:Car:Fuel    1.00 USD
              Assets:Cash

            2016-01-05 * "repair"
              Expenses:Car        10.00 USD
              Assets:Cash

            2016-01-05 * "carpet - not a child of Expenses:Car"
              Expenses:Carpet    100.00 USD
              Assets:Cash
            """),
        encoding="utf-8",
    )
    ledger = FavaLedger(str(ledger_path))
    filtered = ledger.get_filtered()

    (interval,) = ledger.charts.interval_totals(
        filtered, Month, "Expenses:Car", "USD"
    )
    assert interval.balance["USD"] == Decimal("11.00")
    assert set(interval.account_balances) == {
        "Expenses:Car",
        "Expenses:Car:Fuel",
    }

    (interval,) = ledger.charts.interval_totals(
        filtered, Month, "Expenses:Carpet", "USD"
    )
    assert interval.balance["USD"] == Decimal("100.00")
