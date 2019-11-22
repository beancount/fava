# pylint: disable=missing-docstring

from beancount.core.number import D
from flask import g
import pytest

from fava.util.date import Interval


def test_interval_totals(app, small_example_ledger, snapshot):
    with app.test_request_context(""):
        g.conversion = None
        data = small_example_ledger.charts.interval_totals(
            Interval.MONTH, "Expenses"
        )
        snapshot(data)


def test_prices(example_ledger, snapshot):
    data = example_ledger.charts.prices()
    assert all(price[1] for price in data)
    snapshot(data)


def test_linechart_data(app, example_ledger, snapshot):
    with app.test_request_context():
        g.conversion = "units"
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities"
        )
        snapshot(data)
        g.conversion = "at_cost"
        g.ledger = example_ledger
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities"
        )
        snapshot(data)


def test_net_worth(app, example_ledger, snapshot):
    with app.test_request_context():
        app.preprocess_request()
        g.conversion = "USD"
        data = example_ledger.charts.net_worth(Interval.MONTH)
        snapshot(data)


def test_hierarchy(app, example_ledger):
    with app.test_request_context("/"):
        app.preprocess_request()
        data = example_ledger.charts.hierarchy("Assets")
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
    "query,snapshot_id",
    [
        ("select account, sum(position) group by account", "1"),
        ("select joinstr(tags), sum(position) group by joinstr(tags)", "2"),
        ("select date, sum(position) group by date", "3"),
    ],
)
def test_query(example_ledger, snapshot, query, snapshot_id):
    _, types, rows = example_ledger.query_shell.execute_query(query)
    data = example_ledger.charts.query(types, rows)
    snapshot(data, snapshot_id)
