"""Provide data suitable for Fava's charts. """
import datetime

from beancount.core import flags, convert, realization
from beancount.core.amount import Amount
from beancount.core.data import Transaction, Cost
from beancount.core.display_context import DisplayContext
from beancount.core.number import Decimal, MISSING, ZERO
from beancount.core.position import Position
from beancount.core.data import iter_entry_dates
from beancount.utils.misc_utils import filter_type
from flask.json import JSONEncoder

from fava.util import listify, pairwise
from fava.template_filters import cost_or_value
from fava.core.helpers import FavaModule
from fava.core.inventory import CounterInventory
from fava.core.tree import Tree


class FavaJSONEncoder(JSONEncoder):
    """Allow encoding some Beancount date structures."""

    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, (datetime.date, Amount, Position)):
            return str(o)
        elif isinstance(o, (set, frozenset)):
            return list(o)
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            # workaround for #472
            if isinstance(o, DisplayContext):
                o.ccontexts.pop(MISSING, None)
            return str(o)


def _inventory_units(inventory):
    """Renders an the units in an inventory to a currency -> amount dict."""
    return {
        p.units.currency: p.units.number
        for p in inventory.reduce(convert.get_units)
    }


def _serialize_account_node(node, date):
    children = [
        _serialize_account_node(account, date)
        for account in node.children
    ]
    return {
        'account': node.name,
        'balance_children': cost_or_value(node.balance_children),
        'balance': cost_or_value(node.balance),
        'children': children,
    }


class ChartModule(FavaModule):
    """Return data for the various charts in Fava."""
    __slots__ = ['ledger']

    def events(self, event_type=None):
        """All events for a given event type."""
        return [{
            'type': entry.type,
            'date': entry.date,
            'description': entry.description
        } for entry in self.ledger.events(event_type)]

    def hierarchy(self, account_name, begin=None, end=None):
        """An account tree."""
        if begin:
            entries = iter_entry_dates(self.ledger.entries, begin, end)
            tree = Tree(entries)
        else:
            tree = self.ledger.root_tree
        return _serialize_account_node(tree.get(account_name), end)

    @listify
    def interval_totals(self, interval, accounts):
        """Renders totals for account (or accounts) in the intervals.

        Args:
            interval: A string for the interval.
            accounts: A single account (str) or a tuple of accounts.
        """
        for begin, end in pairwise(self.ledger.interval_ends(interval)):
            inventory = CounterInventory()
            entries = iter_entry_dates(self.ledger.entries, begin, end)
            for entry in filter_type(entries, Transaction):
                for posting in entry.postings:
                    if posting.account.startswith(accounts):
                        inventory.add_position(posting)

            yield {
                'begin_date': begin,
                'totals': cost_or_value(inventory, end),
                'budgets':
                self.ledger.budgets.calculate_children(accounts, begin, end),
            }

    def linechart(self, account_name):
        """The balance of an account.

        Args:
            account_name: A string.

        Returns:
            A list of dicts for all dates on which the balance of the given
            account has changed containing the balance (in units) of the
            account at that date.
        """
        real_account = realization.get_or_create(self.ledger.root_account,
                                                 account_name)
        postings = realization.get_postings(real_account)
        journal = realization.iterate_with_balance(postings)

        # When the balance for a commodity just went to zero, it will be
        # missing from the 'balance' field but appear in the 'change' field.
        # Use 0 for those commodities.
        return [{
            'date': entry.date,
            'balance': dict({curr: 0
                             for curr in list(change.currencies())},
                            **_inventory_units(balance)),
        } for entry, _, change, balance in journal if len(change)]

    @listify
    def net_worth(self, interval):
        """Compute net worth.

        Args:
            interval: A string for the interval.

        Returns:
            A list of dicts for all ends of the given interval containing the
            net worth (Assets + Liabilities) separately converted to all
            operating currencies.
        """
        transactions = (entry for entry in self.ledger.entries
                        if (isinstance(entry, Transaction) and entry.flag !=
                            flags.FLAG_UNREALIZED))

        types = (self.ledger.options['name_assets'],
                 self.ledger.options['name_liabilities'])

        txn = next(transactions, None)
        inventory = CounterInventory()

        for date in self.ledger.interval_ends(interval):
            while txn and txn.date < date:
                for posting in filter(lambda p: p.account.startswith(types),
                                      txn.postings):
                    # Since we will be reducing the inventory to the operating
                    # currencies, pre-aggregate the positions to reduce the
                    # number of elements in the inventory.
                    inventory.add_amount(
                        posting.units,
                        Cost(ZERO, posting.cost.currency, None, None)
                        if posting.cost else None)
                txn = next(transactions, None)
            yield {
                'date': date,
                'balance': {
                    currency:
                    inventory.reduce(convert.convert_position, currency,
                                     self.ledger.price_map,
                                     date).get(currency)
                    for currency in self.ledger.options['operating_currency']
                }
            }
