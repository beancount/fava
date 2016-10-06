"""Provide data suitable for Fava's charts. """
from datetime import date, datetime

from beancount.core.amount import Amount, decimal
from beancount.core.position import Position
from beancount.core import inventory, realization
from beancount.core.data import iter_entry_dates
from flask.json import JSONEncoder

from fava.api.helpers import net_worth_at_dates


class BeanJSONEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, Amount):
            return str(o)
        elif isinstance(o, Position):
            return str(o)
        elif isinstance(o, (set, frozenset)):
            return list(o)
        return JSONEncoder.default(self, o)


def serialize_inventory(inventory, at_cost=False):
    """Renders an Inventory to a currency -> amount dict."""
    if at_cost:
        inventory = inventory.cost()
    else:
        inventory = inventory.units()
    return {p.units.currency: p.units.number for p in inventory}


def _real_account(account_name, entries, begin_date, end_date):
    if begin_date:
        entries = list(iter_entry_dates(entries, begin_date, end_date))

    return realization.get_or_create(realization.realize(entries),
                                     account_name)


def serialize_real_account(real_account):
    return {
        'account': real_account.account,
        'balance_children':
            serialize_inventory(realization.compute_balance(real_account),
                                at_cost=True),
        'balance': serialize_inventory(real_account.balance, at_cost=True),
        'children': [serialize_real_account(a)
                     for n, a in sorted(real_account.items())],
    }


class Charts(object):
    __slots__ = ['api']

    def __init__(self, api):
        self.api = api

    def _total_balance(self, names, begin_date, end_date):
        totals = [realization.compute_balance(
            _real_account(account_name, self.api.entries, begin_date,
                          end_date))
                  for account_name in names]
        return serialize_inventory(sum(totals, inventory.Inventory()),
                                   at_cost=True)

    def hierarchy(self, account_name, begin_date=None, end_date=None):
        real_account = _real_account(
            account_name, self.api.entries, begin_date, end_date)
        return serialize_real_account(real_account)

    def interval_totals(self, interval, account_name):
        """Renders totals for account (or accounts) in the intervals."""
        if isinstance(account_name, str):
            names = [account_name]
        else:
            names = account_name

        interval_tuples = self.api._interval_tuples(interval)
        return [{
            'begin_date': begin_date,
            'totals': self._total_balance(
                names,
                begin_date, end_date),
        } for begin_date, end_date in interval_tuples]

    def linechart(self, account_name):
        real_account = realization.get_or_create(self.api.root_account,
                                                 account_name)
        postings = realization.get_postings(real_account)
        journal = realization.iterate_with_balance(postings)

        return [{
            'date': entry.date,
            # when there's no holding for a commodity, it will be missing from
            # 'balance' field but appear in 'change' field. Use 0 for those
            # commodities.
            'balance': dict({curr: 0 for curr in list(change.currencies())},
                            **serialize_inventory(balance)),
        } for entry, _, change, balance in journal if len(change)]

    def net_worth_at_dates(self, interval):
        interval_tuples = self.api._interval_tuples(interval)
        if not interval_tuples:
            return []

        dates = [interval_tuples[0][0]] + [p[1] for p in interval_tuples]

        return net_worth_at_dates(self.api.entries, dates, self.api.price_map,
                                  self.api.options)
