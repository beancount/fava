"""Provide data suitable for Fava's charts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from datetime import date
from datetime import timedelta
from decimal import Decimal
from re import Pattern
from typing import Any
from typing import Iterable
from typing import TYPE_CHECKING

from beancount.core.data import Booking
from beancount.core.data import iter_entry_dates
from beancount.core.number import MISSING
from flask.json.provider import JSONProvider
from simplejson import dumps as simplejson_dumps
from simplejson import loads as simplejson_loads

from fava.beans.abc import Amount
from fava.beans.abc import Position
from fava.beans.abc import Transaction
from fava.beans.account import child_account_tester
from fava.beans.flags import FLAG_UNREALIZED
from fava.core.conversion import cost_or_value
from fava.core.inventory import CounterInventory
from fava.core.module_base import FavaModule
from fava.core.tree import Tree
from fava.util import listify

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FilteredLedger
    from fava.core.conversion import Conversion
    from fava.core.inventory import SimpleCounterInventory
    from fava.core.tree import SerialisedTreeNode
    from fava.util.date import Interval


ONE_DAY = timedelta(days=1)
ZERO = Decimal()


def _json_default(o: Any) -> Any:
    """Specific serialisation for some data types."""
    if isinstance(o, (date, Amount, Booking, Position)):
        return str(o)
    if isinstance(o, (set, frozenset)):
        return list(o)
    if isinstance(o, Pattern):
        return o.pattern
    if is_dataclass(o):
        return {field.name: getattr(o, field.name) for field in fields(o)}
    if o is MISSING:
        return None
    raise TypeError


def dumps(obj: Any, **_kwargs: Any) -> str:
    """Dump as a JSON string."""
    return simplejson_dumps(
        obj,
        indent="  ",
        sort_keys=True,
        default=_json_default,
    )


def loads(s: str | bytes) -> Any:
    """Load a JSON string."""
    return simplejson_loads(s)


class FavaJSONProvider(JSONProvider):
    """Use custom JSON encoder and decoder."""

    def dumps(self, obj: Any, **_kwargs: Any) -> str:  # noqa: D102
        return dumps(obj)

    def loads(self, s: str | bytes, **_kwargs: Any) -> Any:  # noqa: D102
        return simplejson_loads(s)


@dataclass(frozen=True)
class DateAndBalance:
    """Balance at a date."""

    date: date
    balance: SimpleCounterInventory


@dataclass(frozen=True)
class DateAndBalanceWithBudget:
    """Balance at a date with a budget."""

    date: date
    balance: SimpleCounterInventory
    account_balances: dict[str, SimpleCounterInventory]
    budgets: dict[str, Decimal]


class ChartModule(FavaModule):
    """Return data for the various charts in Fava."""

    def hierarchy(
        self,
        filtered: FilteredLedger,
        account_name: str,
        conversion: str | Conversion,
        begin: date | None = None,
        end: date | None = None,
    ) -> SerialisedTreeNode:
        """Render an account tree."""
        if begin is not None and end is not None:
            tree = Tree(iter_entry_dates(filtered.entries, begin, end))
        else:
            tree = filtered.root_tree
        return tree.get(account_name).serialise(
            conversion,
            self.ledger.prices,
            end - ONE_DAY if end is not None else None,
        )

    @listify
    def interval_totals(
        self,
        filtered: FilteredLedger,
        interval: Interval,
        accounts: str | tuple[str, ...],
        conversion: str | Conversion,
        *,
        invert: bool = False,
    ) -> Iterable[DateAndBalanceWithBudget]:
        """Render totals for account (or accounts) in the intervals.

        Args:
            filtered: The filtered ledger.
            interval: An interval.
            accounts: A single account (str) or a tuple of accounts.
            conversion: The conversion to use.
            invert: invert all numbers.

        Yields:
            The balances and budgets for the intervals.
        """
        prices = self.ledger.prices

        # limit the bar charts to 100 intervals
        intervals = filtered.interval_ranges(interval)[-100:]

        for date_range in intervals:
            inventory = CounterInventory()
            entries = iter_entry_dates(
                filtered.entries,
                date_range.begin,
                date_range.end,
            )
            account_inventories: dict[str, CounterInventory] = defaultdict(
                CounterInventory,
            )
            for entry in entries:
                for posting in getattr(entry, "postings", []):
                    if posting.account.startswith(accounts):
                        account_inventories[posting.account].add_position(
                            posting,
                        )
                        inventory.add_position(posting)
            balance = cost_or_value(
                inventory,
                conversion,
                prices,
                date_range.end_inclusive,
            )
            account_balances = {
                account: cost_or_value(
                    acct_value,
                    conversion,
                    prices,
                    date_range.end_inclusive,
                )
                for account, acct_value in account_inventories.items()
            }
            budgets = (
                self.ledger.budgets.calculate_children(
                    accounts,
                    date_range.begin,
                    date_range.end,
                )
                if isinstance(accounts, str)
                else {}
            )

            if invert:
                balance = -balance
                budgets = {k: -v for k, v in budgets.items()}
                account_balances = {k: -v for k, v in account_balances.items()}

            yield DateAndBalanceWithBudget(
                date_range.end_inclusive,
                balance,
                account_balances,
                budgets,
            )

    @listify
    def linechart(
        self,
        filtered: FilteredLedger,
        account_name: str,
        conversion: str | Conversion,
    ) -> Iterable[DateAndBalance]:
        """Get the balance of an account as a line chart.

        Args:
            filtered: The filtered ledger.
            account_name: A string.
            conversion: The conversion to use.

        Yields:
            Dicts for all dates on which the balance of the given
            account has changed containing the balance (in units) of the
            account at that date.
        """

        def _balances() -> Iterable[tuple[date, CounterInventory]]:
            last_date = None
            running_balance = CounterInventory()
            is_child_account = child_account_tester(account_name)

            for entry in filtered.entries:
                for posting in getattr(entry, "postings", []):
                    if is_child_account(posting.account):
                        new_date = entry.date
                        if last_date is not None and new_date > last_date:
                            yield (last_date, running_balance)
                        running_balance.add_position(posting)
                        last_date = new_date

            if last_date is not None:
                yield (last_date, running_balance)

        # When the balance for a commodity just went to zero, it will be
        # missing from the 'balance' so keep track of currencies that last had
        # a balance.
        last_currencies = None
        prices = self.ledger.prices

        for d, running_bal in _balances():
            balance = cost_or_value(running_bal, conversion, prices, d)
            currencies = set(balance.keys())
            if last_currencies:
                for currency in last_currencies - currencies:
                    balance[currency] = ZERO
            last_currencies = currencies
            yield DateAndBalance(d, balance)

    @listify
    def net_worth(
        self,
        filtered: FilteredLedger,
        interval: Interval,
        conversion: str | Conversion,
    ) -> Iterable[DateAndBalance]:
        """Compute net worth.

        Args:
            filtered: The filtered ledger.
            interval: A string for the interval.
            conversion: The conversion to use.

        Yields:
            Dicts for all ends of the given interval containing the
            net worth (Assets + Liabilities) separately converted to all
            operating currencies.
        """
        transactions = (
            entry
            for entry in filtered.entries
            if (
                isinstance(entry, Transaction)
                and entry.flag != FLAG_UNREALIZED
            )
        )

        types = (
            self.ledger.options["name_assets"],
            self.ledger.options["name_liabilities"],
        )

        txn = next(transactions, None)
        inventory = CounterInventory()

        prices = self.ledger.prices
        for date_range in filtered.interval_ranges(interval):
            while txn and txn.date < date_range.end:
                for posting in txn.postings:
                    if posting.account.startswith(types):
                        inventory.add_position(posting)
                txn = next(transactions, None)
            yield DateAndBalance(
                date_range.end_inclusive,
                cost_or_value(
                    inventory,
                    conversion,
                    prices,
                    date_range.end_inclusive,
                ),
            )
