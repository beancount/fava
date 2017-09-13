import datetime

from beancount.core.number import D

from fava.application import app


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


def test_hierarchy(example_ledger):
    with app.test_request_context('/'):
        app.preprocess_request()
        data = example_ledger.charts.hierarchy('Assets')
        assert data['balance_children'] == {'IRAUSD': D('7200.00'),
                                            'USD': D('94320.27840'),
                                            'VACHR': D('-82')}
        assert data['balance'] == {}
        # Assets:US:ETrade
        etrade = data['children'][1]['children'][2]
        assert etrade['children'][1]['balance'] == {'USD': D('4899.98')}
        assert etrade['balance_children'] == {'USD': D('23137.54')}
