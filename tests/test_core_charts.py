# pylint: disable=missing-docstring

from beancount.core.number import D
from flask.json import dumps
import pytest

from fava.core import FavaLedger
from fava.util.date import Interval


def test_interval_totals(
    app, small_example_ledger: FavaLedger, snapshot
) -> None:
    with app.test_request_context():
        data = small_example_ledger.charts.interval_totals(
            Interval.MONTH, "Expenses", "at_cost"
        )
        snapshot(data)
        snapshot(dumps(data))


def test_prices(example_ledger: FavaLedger, snapshot) -> None:
    data = example_ledger.charts.prices()
    assert all(price[1] for price in data)
    snapshot(data)


def test_linechart_data_default(example_ledger: FavaLedger, snapshot) -> None:
    data = example_ledger.charts.linechart(
        "Assets:Testing:MultipleCommodities", "at_cost"
    )
    snapshot(data)


def test_linechart_data_units(example_ledger: FavaLedger, snapshot) -> None:
    data = example_ledger.charts.linechart(
        "Assets:Testing:MultipleCommodities", "units"
    )
    snapshot(data)


def test_linechart_data_at_cost(example_ledger: FavaLedger, snapshot) -> None:
    data = example_ledger.charts.linechart(
        "Assets:Testing:MultipleCommodities", "at_cost"
    )
    snapshot(data)


def test_linechart_data_at_value(
    app, example_ledger: FavaLedger, snapshot
) -> None:
    with app.test_request_context():
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities", "at_value"
        )
        snapshot(data)
        snapshot(dumps(data))


def test_linechart_data_usd(app, example_ledger: FavaLedger, snapshot) -> None:
    with app.test_request_context():
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities", "USD"
        )
        snapshot(data)
        snapshot(dumps(data))


def test_net_worth(app, example_ledger: FavaLedger, snapshot) -> None:
    with app.test_request_context():
        data = example_ledger.charts.net_worth(Interval.MONTH, "USD")
        snapshot(data)
        snapshot(dumps(data))


def test_hierarchy(app, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/"):
        data = example_ledger.charts.hierarchy("Assets", "at_cost")
        assert data["balance_children"] == {
            "IRAUSD": D("7200.00"),
            "USD": D("94320.27840"),
            "VACHR": D("-82"),
        }
        assert data["balance"] == {}
        # Assets:US:ETrade
        etrade = data["children"][0]["children"][2]
        assert etrade["children"][4]["balance"] == {"USD": D("4899.98")}
        assert etrade["balance_children"] == {"USD": D("23137.54")}


@pytest.mark.parametrize(
    "query",
    [
        ("select account, sum(position) group by account"),
        ("select joinstr(tags), sum(position) group by joinstr(tags)"),
        ("select date, sum(position) group by date"),
    ],
)
def test_query(example_ledger: FavaLedger, snapshot, query) -> None:
    _, types, rows = example_ledger.query_shell.execute_query(query)
    data = example_ledger.charts.query(types, rows)
    snapshot(data)
