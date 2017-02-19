from beancount.core import flags, account_types, convert
from beancount.core.data import Transaction
from beancount.core.inventory import Inventory
from beancount.parser import options


def inventory_at_dates(transactions, dates, posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    The inventory for a date includes all matching postings PRIOR to it.

    Args:
      transactions: list of transactions, sorted by date.
      dates: iterator of dates
      posting_predicate: predicate with the Transaction and Posting to
        decide whether to include the posting in the inventory.
    """

    iterator = iter(transactions)
    txn = next(iterator, None)

    inventory = Inventory()

    for date in dates:
        while txn and txn.date < date:
            for posting in filter(posting_predicate, txn.postings):
                inventory.add_position(posting)
            txn = next(iterator, None)
        yield inventory


def net_worth_at_dates(entries, dates, price_map, options_map):
    transactions = [entry for entry in entries
                    if (isinstance(entry, Transaction) and
                        entry.flag != flags.FLAG_UNREALIZED)]

    types = options.get_account_types(options_map)

    def _posting_predicate(posting):
        account_type = account_types.get_account_type(posting.account)
        if account_type in (types.assets, types.liabilities):
            return True

    inventories = inventory_at_dates(transactions, dates, _posting_predicate)

    return [{
        'date': date,
        'balance': {
            currency: inv.reduce(convert.convert_position, currency, price_map,
                                 date).get_currency_units(currency).number
            for currency in options_map['operating_currency']
        }
    } for date, inv in zip(dates, inventories)]
