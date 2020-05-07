"""Provide data suitable for Fava's charts. """
import datetime
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from beancount.core import flags
from beancount.core import realization
from beancount.core.amount import Amount
from beancount.core.data import iter_entry_dates
from beancount.core.data import Transaction
from beancount.core.inventory import Inventory
from beancount.core.number import Decimal
from beancount.core.position import Position
from flask.json import JSONEncoder

from fava.core.module_base import FavaModule
from fava.core.tree import Tree
from fava.helpers import FavaAPIException
from fava.template_filters import cost_or_value
from fava.template_filters import units
from fava.util import listify
from fava.util import pairwise
from fava.util.date import Interval


def inv_to_dict(inventory):
    """Convert an inventory to a simple cost->number dict."""
    return {pos.units.currency: pos.units.number for pos in inventory}


Inventory.for_json = inv_to_dict  # type: ignore


class FavaJSONEncoder(JSONEncoder):
    """Allow encoding some Beancount date structures."""

    def __init__(self, *args, **kwargs):
        # Allow use of a `for_json` method to serialise dict subclasses.
        kwargs["for_json"] = True
        super().__init__(*args, **kwargs)

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

    def hierarchy(
        self,
        account_name: str,
        begin: Optional[datetime.date] = None,
        end: Optional[datetime.date] = None,
    ):
        """An account tree."""
        if begin is not None:
            tree = Tree(iter_entry_dates(self.ledger.entries, begin, end))
        else:
            tree = self.ledger.root_tree
        return tree.get(account_name).serialise(end)

    @listify
    def prices(
        self,
    ) -> Generator[
        Tuple[str, str, List[Tuple[datetime.date, Decimal]]], None, None
    ]:
        """The prices for all commodity pairs.

        Returns:
            A list of tuples (base, quote, prices) where prices
            is a list of prices.
        """
        for base, quote in self.ledger.commodity_pairs():
            prices = self.ledger.prices(base, quote)
            if prices:
                yield base, quote, prices

    @listify
    def interval_totals(
        self, interval: Interval, accounts: Union[str, Tuple[str]]
    ):
        """Renders totals for account (or accounts) in the intervals.

        Args:
            interval: An interval.
            accounts: A single account (str) or a tuple of accounts.
        """
        for begin, end in pairwise(self.ledger.interval_ends(interval)):
            inventory = Inventory()
            entries = iter_entry_dates(self.ledger.entries, begin, end)
            for entry in (e for e in entries if isinstance(e, Transaction)):
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

            balance = inv_to_dict(cost_or_value(balance, entry.date))

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
        inventory = Inventory()

        for end_date_exclusive in self.ledger.interval_ends(interval):
            end_date_inclusive = end_date_exclusive - datetime.timedelta(
                days=1
            )
            while txn and txn.date < end_date_exclusive:
                for posting in txn.postings:
                    if posting.account.startswith(types):
                        inventory.add_position(posting)
                txn = next(transactions, None)
            yield {
                "date": end_date_exclusive,
                "balance": cost_or_value(inventory, end_date_inclusive),
            }

    @staticmethod
    def can_plot_query(types):
        """Whether we can plot the given query.

        Args:
            types: The list of types returned by the BQL query.
        """
        return (
            len(types) == 2
            and types[0][1] in {str, datetime.date}
            and types[1][1] is Inventory
        )

    def query(self, types, rows):
        """Chart for a query.

        Args:
            types: The list of result row types.
            rows: The result rows.
        """

        if not self.can_plot_query(types):
            raise FavaAPIException("Can not plot the given chart.")
        if types[0][1] is datetime.date:
            return [
                {"date": date, "balance": units(inv)} for date, inv in rows
            ]
        return [{"group": group, "balance": units(inv)} for group, inv in rows]
