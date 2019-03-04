"""Provide data suitable for Fava's charts. """
import datetime

from flask.json import JSONEncoder
from beancount.core import flags, realization
from beancount.core.amount import Amount
from beancount.core.data import Transaction, iter_entry_dates
from beancount.core.number import Decimal
from beancount.core.position import Position
from beancount.utils.misc_utils import filter_type

from fava.util import listify, pairwise
from fava.template_filters import cost_or_value
from fava.core.helpers import FavaModule
from fava.core.inventory import CounterInventory
from fava.core.tree import Tree


class FavaJSONEncoder(JSONEncoder):
    """Allow encoding some Beancount date structures."""

    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime.date, Amount, Position)):
            return str(o)
        if isinstance(o, (set, frozenset)):
            return list(o)
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


class ChartModule(FavaModule):
    """Return data for the various charts in Fava."""

    __slots__ = ["ledger"]

    def events(self, event_type=None):
        """All events for a given event type."""
        return [
            {
                "type": entry.type,
                "date": entry.date,
                "description": entry.description,
            }
            for entry in self.ledger.events(event_type)
        ]

    def hierarchy(self, account_name, begin=None, end=None):
        """An account tree."""
        if begin:
            tree = Tree(iter_entry_dates(self.ledger.entries, begin, end))
        else:
            tree = self.ledger.root_tree
        return tree.get(account_name).serialise(end)

    @listify
    def interval_totals(self, interval, accounts):
        """Renders totals for account (or accounts) in the intervals.

        Args:
            interval: An interval.
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
                "date": begin,
                "balance": cost_or_value(inventory, end),
                "budgets": self.ledger.budgets.calculate_children(
                    accounts, begin, end
                ),
            }

    @listify
    def linechart(self, account_name):
        """The balance of an account.

        Args:
            account_name: A string.

        Returns:
            A list of dicts for all dates on which the balance of the given
            account has changed containing the balance (in units) of the
            account at that date.
        """
        real_account = realization.get_or_create(
            self.ledger.root_account, account_name
        )
        postings = realization.get_postings(real_account)
        journal = realization.iterate_with_balance(postings)

        # When the balance for a commodity just went to zero, it will be
        # missing from the 'balance' so keep track of currencies that last had
        # a balance.
        last_currencies = None

        for entry, _, change, balance in journal:
            if change.is_empty():
                continue

            balance = {
                p.units.currency: p.units.number
                for p in cost_or_value(balance, entry.date)
            }

            currencies = set(balance.keys())
            if last_currencies:
                for currency in last_currencies - currencies:
                    balance[currency] = 0
            last_currencies = currencies

            yield {"date": entry.date, "balance": balance}

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
        transactions = (
            entry
            for entry in self.ledger.entries
            if (
                isinstance(entry, Transaction)
                and entry.flag != flags.FLAG_UNREALIZED
            )
        )

        types = (
            self.ledger.options["name_assets"],
            self.ledger.options["name_liabilities"],
        )

        txn = next(transactions, None)
        inventory = CounterInventory()

        for date in self.ledger.interval_ends(interval):
            while txn and txn.date < date:
                for posting in filter(
                    lambda p: p.account.startswith(types), txn.postings
                ):
                    inventory.add_position(posting)
                txn = next(transactions, None)
            yield {"date": date, "balance": cost_or_value(inventory, date)}
