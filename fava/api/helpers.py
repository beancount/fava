import operator

from beancount.core import account, flags, account_types, realization
from beancount.core.number import ZERO
from beancount.ops import prices
from beancount.core.data import Posting, Transaction
from beancount.core.amount import Amount
from beancount.core.position import Cost
from beancount.core.inventory import Inventory
from beancount.parser import options
from beancount.utils import misc_utils


# Nearly the same as the function of the same name in
# beancount:src/python/beancount/ops/holdings.py but using Postings instead.
def get_final_holdings(entries, included_account_types=None, price_map=None,
                       date=None):
    """Get a list of holdings by account (as Postings)."""

    simple_entries = [entry for entry in entries
                      if (not isinstance(entry, Transaction) or
                          entry.flag != flags.FLAG_UNREALIZED)]

    root_account = realization.realize(simple_entries)

    holdings = []

    for real_account in sorted(list(realization.iter_children(root_account)),
                               key=lambda ra: ra.account):
        account_type = account_types.get_account_type(real_account.account)
        if (included_account_types and
                account_type not in included_account_types):
            continue
        for pos in real_account.balance:
            price = None
            if pos.cost and price_map:
                base_quote = (pos.units.currency, pos.cost.currency)
                _, price = prices.get_price(price_map, base_quote, date)
            holdings.append(Posting(real_account.account,
                                    pos.units,
                                    pos.cost,
                                    price, None, None))

    return holdings


# Nearly the same as the function of the same name in
# beancount:src/python/beancount/ops/holdings.py but using Postings instead.
def aggregate_holdings_list(holdings):
    if not holdings:
        return None

    units, total_book_value, total_market_value = ZERO, ZERO, ZERO
    accounts = set()
    currencies = set()
    cost_currencies = set()
    for pos in holdings:
        units += pos.units.number
        accounts.add(pos.account)
        currencies.add(pos.units.currency)
        cost_currencies.add(
            pos.cost.currency if pos.cost else pos.units.currency)

        if pos.cost:
            total_book_value += pos.units.number * pos.cost.number
        else:
            total_book_value += pos.units.number

        if pos.price is not None:
            total_market_value += pos.units.number * pos.price
        else:
            total_market_value += \
                pos.units.number * (pos.cost.number if pos.cost else 1)

    assert len(cost_currencies) == 1

    avg_cost = total_book_value / units if units else None
    avg_price = total_market_value / units if units else None

    currency = currencies.pop() if len(currencies) == 1 else '*'
    cost_currency = cost_currencies.pop()
    account_ = (accounts.pop() if len(accounts) == 1
                else account.commonprefix(accounts))
    show_cost = bool(avg_cost) and cost_currency != currency

    return Posting(
        account_,
        Amount(units, currency),
        Cost(avg_cost, cost_currency, None, None) if show_cost else None,
        avg_price if show_cost else None,
        None,
        None
    )


def aggregate_holdings_by(holdings, aggregation_key):
    """Aggregate holdings by the given key.

    They are always grouped by cost currency.
    """

    if aggregation_key == 'currency':
        def key(pos):
            return (pos.units.currency,
                    pos.cost.currency if pos.cost else pos.units.currency)
    elif aggregation_key == 'account':
        def key(pos):
            return (pos.account,
                    pos.cost.currency if pos.cost else pos.units.currency)
    else:
        def key(pos):
            return pos.cost.currency if pos.cost else pos.units.currency

    aggregated_holdings = [aggregate_holdings_list(holdings)
                           for _, holdings in
                           misc_utils.groupby(key, holdings).items()]

    return sorted(aggregated_holdings,
                  key=operator.attrgetter('account', 'units.currency'))


def inventory_at_dates(transactions, dates, posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    The inventory for a date includes all matching postings PRIOR to it.

    Args:
      transactions: list of transactions, sorted by date.
      dates: iterator of dates
      posting_predicate: predicate with the Transaction and Posting to
        decide whether to include the posting in the inventory.
    """
    if not transactions:
        return

    iterator = iter(transactions)
    txn = next(iterator)

    inventory = Inventory()

    for date in dates:
        while txn.date < date:
            for posting in txn.postings:
                if posting_predicate(posting):
                    inventory.add_position(posting)
            try:
                txn = next(iterator)
            except StopIteration:
                break
        yield inventory.get_positions()


def convert_inventory(price_map, target_currency, inventory, date):
    """Convert and sum an inventory to a common currency.

    Returns:
      A Decimal, the sum of all positions that could be converted.
    """

    total = ZERO

    for pos in inventory:
        # Fetch the price in the cost currency if there is one.
        if pos.cost:
            base_quote = (pos.units.currency, pos.cost.currency)
            _, cost_number = prices.get_price(price_map, base_quote, date)
            if cost_number is None:
                cost_number = pos.cost.number
            currency = pos.cost.currency
        # Otherwise, price it in its own currency.
        else:
            cost_number = 1
            currency = pos.units.currency
        if currency == target_currency:
            total += pos.units.number * cost_number
        else:
            base_quote = (currency, target_currency)

            # Get the conversion rate.
            _, price = prices.get_price(price_map, base_quote, date)
            if price is not None:
                total += pos.units.number * cost_number * price
    return total


def net_worth_at_dates(entries, dates, price_map, options_map):
    transactions = [entry for entry in entries
                    if (isinstance(entry, Transaction) and
                        entry.flag != flags.FLAG_UNREALIZED)]

    types = options.get_account_types(options_map)

    def posting_predicate(posting):
        account_type = account_types.get_account_type(posting.account)
        if account_type in (types.assets, types.liabilities):
            return True

    inventories = inventory_at_dates(transactions, dates, posting_predicate)

    return [{
        'date': date,
        'balance': {
            currency: convert_inventory(price_map, currency, inv, date)
            for currency in options_map['operating_currency']
        }
    } for date, inv in zip(dates, inventories)]
