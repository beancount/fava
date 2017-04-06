import datetime

from beancount.core.number import D


def test_linechart_data(example_ledger):
    data = example_ledger.charts.linechart(
        'Assets:Testing:MultipleCommodities')
    assert data[1]['balance']['USD'] == 50
    assert data[2]['balance']['USD'] == 0


def test_net_worth(example_ledger):
    data = example_ledger.charts.net_worth('month')
    assert data[-18]['date'] == datetime.date(2015, 1, 1)
    assert data[-18]['balance']['USD'] == D('39125.34004')
    assert data[-1]['date'] == datetime.date(2016, 5, 10)
    assert data[-1]['balance']['USD'] == D('102327.53144')
