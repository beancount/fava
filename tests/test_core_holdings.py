import datetime

from beancount.core.data import Posting, Transaction
from beancount.core.amount import A, Amount
from beancount.core.number import D
from beancount.core.position import Cost
from beancount.ops import prices

from fava.core.holdings import (inventory_at_dates, get_final_holdings,
                                aggregate_holdings_list, aggregate_holdings_by)


def test_get_final_holdings(load_doc):
    """
    2013-04-05 *
      Equity:Unknown
      Assets:Cash			50000 USD

    2013-04-01 *
      Assets:Account1             15 HOOL {518.73 USD}
      Assets:Cash

    2013-04-02 *
      Assets:Account1             10 HOOL {523.46 USD}
      Assets:Cash

    2013-04-03 *
      Assets:Account1             -4 HOOL {518.73 USD}
      Assets:Cash

    2013-04-02 *
      Assets:Account2            20 ITOT {85.195 USD}
      Assets:Cash

    2013-04-03 *
      Assets:Account3             50 HOOL {540.00 USD} @ 560.00 USD
      Assets:Cash

    2013-04-10 *
      Assets:Cash			5111 USD
      Liabilities:Loan
    """
    entries, _, _ = load_doc

    holdings = get_final_holdings(entries)
    holdings = sorted(map(tuple, holdings))

    assert holdings == [
        ('Assets:Account1', A('10 HOOL'), Cost(D('523.46'), 'USD', None, None),
         None, None, None),
        ('Assets:Account1', A('11 HOOL'), Cost(D('518.73'), 'USD', None, None),
         None, None, None),
        ('Assets:Account2', A('20 ITOT'), Cost(D('85.195'), 'USD', None, None),
         None, None, None),
        ('Assets:Account3', A('50 HOOL'), Cost(D('540.00'), 'USD', None, None),
         None, None, None),
        ('Assets:Cash', A('15466.470 USD'), None, None, None, None),
        ('Equity:Unknown', A('-50000 USD'), None, None, None, None),
        ('Liabilities:Loan', A('-5111 USD'), None, None, None, None),
    ]

    holdings = get_final_holdings(entries, ('Assets'))
    holdings = sorted(map(tuple, holdings))

    assert holdings == [
        ('Assets:Account1', A('10 HOOL'), Cost(D('523.46'), 'USD', None, None),
         None, None, None),
        ('Assets:Account1', A('11 HOOL'), Cost(D('518.73'), 'USD', None, None),
         None, None, None),
        ('Assets:Account2', A('20 ITOT'), Cost(D('85.195'), 'USD', None, None),
         None, None, None),
        ('Assets:Account3', A('50 HOOL'), Cost(D('540.00'), 'USD', None, None),
         None, None, None),
        ('Assets:Cash', A('15466.470 USD'), None, None, None, None),
    ]


def test_holdings_with_prices(load_doc):
    """
    2013-04-05 *
      Equity:Unknown
      Assets:Cash			50000 USD

    2013-04-01 *
      Assets:Account1             15 HOOL {518.73 USD}
      Assets:Cash

    2013-06-01 price HOOL  578.02 USD

    """
    entries, _, _ = load_doc
    price_map = prices.build_price_map(entries)

    holdings = get_final_holdings(entries, ('Assets'), price_map)
    holdings = sorted(map(tuple, holdings))

    assert holdings == [
        ('Assets:Account1', A('15 HOOL'), Cost(D('518.73'), 'USD', None, None),
         D('578.02'), None, None),
        ('Assets:Cash', A('42219.05 USD'), None, None, None, None),
    ]


def test_holdings_zero_position(load_doc):
    """
    2012-07-02 ! "I received 1 new share in dividend, without paying"
      Assets:Stocks:NYA 1 NYA {0 EUR}
      Income:Dividends:NYA -0 EUR

    2014-11-13 balance Assets:Stocks:NYA 1 NYA
    """
    entries, _, _ = load_doc
    price_map = prices.build_price_map(entries)
    holdings = get_final_holdings(entries, ('Assets', 'Liabilities'),
                                  price_map)
    assert len(holdings) == 1
    assert holdings[0].cost.currency == 'EUR'


def test_aggregate_holdings_list_simple():
    assert aggregate_holdings_list([]) is None

    holdings = [
        Posting('Assets', A('10 HOOL'), None, None, None, None),
        Posting('Assets', A('14 HOOL'), None, None, None, None),
    ]
    assert aggregate_holdings_list(holdings) == \
        Posting('Assets', A('24 HOOL'), None, None, None, None)

    holdings = [
        Posting('Assets:No', A('10 HOOL'), None, None, None, None),
        Posting('Assets:Test', A('14 HOOL'), None, None, None, None),
    ]
    assert aggregate_holdings_list(holdings) == \
        Posting('Assets', A('24 HOOL'), None, None, None, None)


def test_aggregate_holdings_list_with_cost():
    holdings = [
        Posting('Assets', A('10 HOOL'), None, None, None, None),
        Posting('Assets', A('14 TEST'), Cost(D('10'), 'HOOL', None, None),
                None, None, None),
    ]
    assert aggregate_holdings_list(holdings) == \
        Posting('Assets', Amount(D('24'), '*'),
                Cost(D('6.25'), 'HOOL', None, None),
                D('150') / 24, None, None)


def test_aggregate_holdings_list_with_price():
    holdings = [
        Posting('Assets', A('10 HOOL'), None, None, None, None),
        Posting('Assets', A('14 TEST'), Cost(D('10'), 'HOOL', None, None),
                D('12'), None, None),
    ]
    assert aggregate_holdings_list(holdings) == \
        Posting('Assets', Amount(D('24'), '*'),
                Cost(D('6.25'), 'HOOL', None, None),
                D('178') / 24, None, None)


def test_aggregate_holdings_by():
    assert aggregate_holdings_list([]) is None

    holdings = [
        Posting('Assets', A('10 HOOL'), None, None, None, None),
        Posting('Assets:Test', A('14 HOL'), None, None, None, None),
    ]
    assert aggregate_holdings_by(holdings, 'account') == holdings
    assert aggregate_holdings_by(holdings, 'currency') == holdings
    assert aggregate_holdings_by(holdings, 'invalid') == holdings

    holdings = [
        Posting('Assets', A('10 HOOL'), None, None, None, None),
        Posting('Assets', A('14 HOOL'), None, None, None, None),
    ]
    assert aggregate_holdings_by(holdings, 'account') == \
        [aggregate_holdings_list(holdings)]


def test_inventory_at_dates(load_doc):
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
    entries, _, _ = load_doc
    dates = [
        datetime.date(2016, 1, 1),
        datetime.date(2016, 1, 2),
        datetime.date(2016, 1, 3),
        datetime.date(2016, 1, 4),
        datetime.date(2016, 1, 5),
        datetime.date(2016, 1, 6),
    ]

    transactions = [
        entry for entry in entries if isinstance(entry, Transaction)]

    def predicate(posting):
        return True
    number_of_positions = list(
        map(len, list(inventory_at_dates(transactions, dates, predicate))))
    assert number_of_positions == [0, 0, 2, 3, 3, 3]

    def predicate(posting):
        return posting.account.startswith('Assets')
    number_of_positions = list(
        map(len, list(inventory_at_dates(transactions, dates, predicate))))
    assert number_of_positions == [0, 1, 2, 3, 3, 3]
