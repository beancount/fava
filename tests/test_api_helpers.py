import datetime

from beancount.core.position import Cost, Position
from beancount.core.amount import A
from beancount.core.number import D
from beancount.ops.holdings import Holding
from beancount.ops import prices

from fava.api.helpers import get_holding_from_position, holdings_at_dates


def test_get_holding_from_position_without_cost():
    assert get_holding_from_position(Position(A('10 EUR'), None)) == \
        Holding(None, D('10'), 'EUR', None, 'EUR', D('10'), D('10'), None,
                None)


def test_get_holding_from_position_with_cost():
    assert get_holding_from_position(
        Position(A('10 EUR'), Cost(D('1.23'), 'USD', None, None))) == \
        Holding(None, D('10'), 'EUR', D('1.23'), 'USD', D('12.3'), None, None,
                None)


def test_holdings_at_dates(load_doc):
    """
    plugin "auto_accounts"

    2016-01-01 *
      Equity:Unknown
      Assets:Cash			5000 USD

    2016-01-02 *
      Assets:Account1             15 HOOL {123 USD}
      Assets:Cash

    2016-01-03 *
      Assets:Account1             10 HOOL {130 USD}
      Assets:Cash
    """
    entries, errors, options = load_doc
    price_map = prices.build_price_map(entries)
    dates = [
        datetime.date(2016, 1, 1),
        datetime.date(2016, 1, 2),
        datetime.date(2016, 1, 3),
        datetime.date(2016, 1, 4),
    ]
    number_of_holdings = list(
        map(len, list(holdings_at_dates(entries, dates, price_map, options))))
    assert number_of_holdings == [0, 1, 2, 3]
