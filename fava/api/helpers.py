from beancount.core import flags, account_types
from beancount.ops.holdings import Holding
from beancount.core.data import Transaction
from beancount.core.inventory import Inventory
from beancount.parser import options
from beancount.ops import prices


# This really belongs in beancount:src/python/beancount/ops/holdings.py
def get_holding_from_position(position, price_map=None, date=None):
    """Compute a Holding corresponding to the specified position 'pos'.

    :param position: A Position object.
    :param price_map: A dict of prices, as built by prices.build_price_map().
    :param date: A datetime.date instance, the date at which to price the
        holdings.  If left unspecified, we use the latest price information.

    :return: A Holding object.
    """
    if position.cost is not None:
        # Get price information if we have a price_map.
        market_value = None
        if price_map is not None:
            base_quote = (position.units.currency, position.cost.currency)
            price_date, price_number = prices.get_price(price_map,
                                                        base_quote, date)
            if price_number is not None:
                market_value = position.units.number * price_number
        else:
            price_date, price_number = None, None

        return Holding(None,
                       position.units.number,
                       position.units.currency,
                       position.cost.number,
                       position.cost.currency,
                       position.units.number * position.cost.number,
                       market_value,
                       price_number,
                       price_date)
    else:
        return Holding(None,
                       position.units.number,
                       position.units.currency,
                       None,
                       position.units.currency,
                       position.units.number,
                       position.units.number,
                       None,
                       None)


def inventory_at_dates(transactions, dates, posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    The inventory for a specified date includes all matching postings PRIOR to
    it.

    :param transactions: list of transactions, sorted by date.
    :param dates: iterator of dates
    :param posting_predicate: predicate with the Transaction and Posting to
        decide whether to include the posting in the inventory.
    """
    index = 0
    length = len(transactions)

    # inventory maps lot to amount
    inventory = Inventory()
    prev_date = None
    for date in dates:
        assert prev_date is None or date > prev_date
        prev_date = date
        while index < length and transactions[index].date < date:
            entry = transactions[index]
            index += 1
            for posting in entry.postings:
                if posting_predicate(posting):
                    inventory.add_position(posting)
        yield inventory


def holdings_at_dates(entries, dates, price_map, options_map):
    """Computes aggregate holdings at mulitple dates.

    Yields for each date the list of Holding objects.  The holdings are
    aggregated across accounts; the Holding objects will have the account field
    set to None.

    :param entries: The list of entries.
    :param dates: The list of dates.
    :param price_map: A dict of prices, as built by prices.build_price_map().
    :param options_map: The account options.
    """
    transactions = [entry for entry in entries
                    if (isinstance(entry, Transaction) and
                        entry.flag != flags.FLAG_UNREALIZED)]

    types = options.get_account_types(options_map)

    def posting_predicate(posting):
        account_type = account_types.get_account_type(posting.account)
        if account_type in (types.assets, types.liabilities):
            return True

    for date, inventory in zip(dates,
                               inventory_at_dates(transactions, dates,
                                                  posting_predicate)):
        yield [get_holding_from_position(position, price_map, date)
               for position in inventory]
