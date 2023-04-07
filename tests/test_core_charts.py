# pylint: disable=missing-docstring
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from fava.core.charts import pretty_dumps
from fava.util.date import Interval

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

    from .conftest import SnapshotFunc


def test_interval_totals(
    small_example_ledger: FavaLedger, snapshot: SnapshotFunc
) -> None:
    filtered = small_example_ledger.get_filtered()
    for conversion in ["at_cost", "USD"]:
        data = small_example_ledger.charts.interval_totals(
            filtered, Interval.MONTH, "Expenses", conversion
        )
        snapshot(pretty_dumps(data))


def test_interval_totals_inverted(
    small_example_ledger: FavaLedger, snapshot: SnapshotFunc
) -> None:
    filtered = small_example_ledger.get_filtered()
    for conversion in ["at_cost", "USD"]:
        data = small_example_ledger.charts.interval_totals(
            filtered, Interval.MONTH, "Expenses", conversion, invert=True
        )
        snapshot(pretty_dumps(data))


def test_linechart_data(
    example_ledger: FavaLedger, snapshot: SnapshotFunc
) -> None:
    filtered = example_ledger.get_filtered()
    for conversion in ["at_cost", "units", "at_value", "USD"]:
        data = example_ledger.charts.linechart(
            filtered, "Assets:Testing:MultipleCommodities", conversion
        )
        snapshot(pretty_dumps(data))


def test_net_worth(example_ledger: FavaLedger, snapshot: SnapshotFunc) -> None:
    filtered = example_ledger.get_filtered()
    data = example_ledger.charts.net_worth(filtered, Interval.MONTH, "USD")
    snapshot(pretty_dumps(data))


def test_hierarchy(example_ledger: FavaLedger) -> None:
    filtered = example_ledger.get_filtered()
    data = example_ledger.charts.hierarchy(filtered, "Assets", "at_cost")
    assert data.balance_children == {
        "IRAUSD": Decimal("7200.00"),
        "USD": Decimal("94320.27840"),
        "VACHR": Decimal("-82"),
    }
    assert data.balance == {}
    # Assets:US:ETrade
    etrade = data.children[0].children[2]
    assert etrade.children[4].balance == {"USD": Decimal("4899.98")}
    assert etrade.balance_children == {"USD": Decimal("23137.54")}


@pytest.mark.parametrize(
    "query",
    [
        ("select account, sum(position) group by account"),
        ("select joinstr(tags), sum(position) group by joinstr(tags)"),
        ("select date, sum(position) group by date"),
    ],
)
def test_query(
    example_ledger: FavaLedger, snapshot: SnapshotFunc, query: str
) -> None:
    _, types, rows = example_ledger.query_shell.execute_query(
        example_ledger.all_entries, query
    )
    data = example_ledger.charts.query(types, rows)
    snapshot(pretty_dumps(data))
