from datetime import timedelta
import re
import collections

from beancount.core import flags
from beancount.ops.holdings import Holding
from beancount.core.number import ZERO
from beancount.core.data import Transaction
from beancount.parser import options
from beancount.ops import prices
from beancount.utils import bisect_key


def entries_in_inclusive_range(entries, begin_date=None, end_date=None):
    """
    Returns the list of entries satisfying begin_date <= date <= end_date.
    """
    get_date = lambda x: x.date
    if begin_date is None:
        begin_index = 0
    else:
        begin_index = bisect_key.bisect_left_with_key(entries, begin_date,
                                                      key=get_date)
    if end_date is None:
        end_index = len(entries)
    else:
        end_index = bisect_key.bisect_left_with_key(entries,
                                                    end_date+timedelta(days=1),
                                                    key=get_date)
    return entries[begin_index:end_index]


# This really belongs in beancount:src/python/beancount/ops/holdings.py
def get_holding_from_position(lot, number, account=None, price_map=None,
                              date=None):
    """Compute a Holding corresponding to the specified position 'pos'.

    :param lot: A Lot object.
    :param number: The number of units of 'lot' in the position.
    :param account: A str, the name of the account, or None if not needed.
    :param price_map: A dict of prices, as built by prices.build_price_map().
    :param date: A datetime.date instance, the date at which to price the
        holdings.  If left unspecified, we use the latest price information.

    :return: A Holding object.
    """
    if lot.cost is not None:
        # Get price information if we have a price_map.
        market_value = None
        if price_map is not None:
            base_quote = (lot.currency, lot.cost.currency)
            price_date, price_number = prices.get_price(price_map,
                                                        base_quote, date)
            if price_number is not None:
                market_value = number * price_number
        else:
            price_date, price_number = None, None

        return Holding(account,
                       number,
                       lot.currency,
                       lot.cost.number,
                       lot.cost.currency,
                       number * lot.cost.number,
                       market_value,
                       price_number,
                       price_date)
    else:
        return Holding(account,
                       number,
                       lot.currency,
                       None,
                       lot.currency,
                       number,
                       number,
                       None,
                       None)


def inventory_at_dates(entries, dates, transaction_predicate,
                       posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    The inventory for a specified date includes all matching postings PRIOR to
    it.

    :param entries: list of entries, sorted by date.
    :param dates: iterator of dates
    :param transaction_predicate: predicate called on each Transaction entry to
        decide whether to include its postings in the inventory.
    :param posting_predicate: predicate with the Transaction and Posting to
        decide whether to include the posting in the inventory.
    """
    entry_i = 0
    num_entries = len(entries)

    # inventory maps lot to amount
    inventory = collections.defaultdict(lambda: ZERO)
    prev_date = None
    for date in dates:
        assert prev_date is None or date >= prev_date
        prev_date = date
        while entry_i < num_entries and entries[entry_i].date < date:
            entry = entries[entry_i]
            entry_i += 1
            if isinstance(entry, Transaction) and transaction_predicate(entry):
                for posting in entry.postings:
                    if posting_predicate(entry, posting):
                        old_value = inventory[posting.position.lot]
                        new_value = old_value + posting.position.number
                        if new_value == ZERO:
                            del inventory[posting.position.lot]
                        else:
                            inventory[posting.position.lot] = new_value
        yield inventory


def account_descendants_re_pattern(*roots):
    """Returns pattern for matching descendant accounts.

    :param roots: The list of parent account names.  These should not
        end with a ':'.

    :return: The regular expression pattern for matching descendants of
             the specified parents, or those parents themselves.
    """
    return '|'.join('(?:^' + re.escape(name) + '(?::|$))' for name in roots)


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
    account_types = options.get_account_types(options_map)
    FLAG_UNREALIZED = flags.FLAG_UNREALIZED
    transaction_predicate = lambda e: e.flag != FLAG_UNREALIZED
    account_re = re.compile(account_descendants_re_pattern(
        account_types.assets,
        account_types.liabilities))
    posting_predicate = lambda e, p: account_re.match(p.account)
    for date, inventory in zip(dates,
                               inventory_at_dates(
                                   entries, dates,
                                   transaction_predicate = transaction_predicate,
                                   posting_predicate = posting_predicate)):
        yield [get_holding_from_position(lot, number, price_map=price_map, date=date)
               for lot, number in inventory.items()]
