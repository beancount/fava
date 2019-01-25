# pylint: disable=missing-docstring

import datetime
from collections import Counter

from beancount.core.number import D
from flask import g

from fava.util.date import Interval


def test_interval_totals(app, small_example_ledger):
    with app.test_request_context(""):
        g.conversion = None
        data = small_example_ledger.charts.interval_totals(
            Interval.MONTH, "Expenses"
        )
        assert data == [
            {
                "date": datetime.date(2012, 11, 18),
                "balance": {"EUR": D("280.00")},
                "budgets": Counter(
                    {"EUR": D("31.42857142857142857142857145")}
                ),
            },
            {
                "date": datetime.date(2012, 12, 1),
                "balance": {"EUR": D("80.00")},
                "budgets": Counter(
                    {"EUR": D("48.57142857142857142857142861")}
                ),
            },
        ]


def test_linechart_data(app, example_ledger):
    result = [
        {"date": datetime.date(2000, 1, 1), "balance": {"USD": D("100")}},
        {
            "date": datetime.date(2000, 1, 2),
            "balance": {"XYZ": D("1"), "USD": D("50")},
        },
        {
            "date": datetime.date(2000, 1, 3),
            "balance": {"USD": 0, "ABC": D("1"), "XYZ": D("1")},
        },
    ]
    with app.test_request_context():
        g.conversion = "units"
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities"
        )
        assert data == result
        g.conversion = "at_cost"
        g.ledger = example_ledger
        data = example_ledger.charts.linechart(
            "Assets:Testing:MultipleCommodities"
        )
        assert data == result


def test_net_worth(app, example_ledger):
    with app.test_request_context():
        app.preprocess_request()
        g.conversion = "USD"
        data = example_ledger.charts.net_worth(Interval.MONTH)
        assert data[-18]["date"] == datetime.date(2015, 1, 1)
        assert data[-18]["balance"]["USD"] == D("39125.34004")
        assert data[-1]["date"] == datetime.date(2016, 5, 10)
        assert data[-1]["balance"]["USD"] == D("102327.53144")


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
