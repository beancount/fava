import datetime

from beancount.core.data import Transaction

from fava.core.holdings import inventory_at_dates


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
        entry for entry in entries if isinstance(entry, Transaction)
    ]

    number_of_positions = [
        len(inv)
        for inv in inventory_at_dates(transactions, dates, lambda p: True)
    ]
    assert number_of_positions == [0, 0, 2, 3, 3, 3]

    number_of_positions = [
        len(inv)
        for inv in inventory_at_dates(transactions, dates,
                                      lambda p: p.account.startswith('Assets'))
    ]
    assert number_of_positions == [0, 1, 2, 3, 3, 3]
