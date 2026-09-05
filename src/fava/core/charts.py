"""Provide data suitable for Fava's charts."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from re import Pattern
from typing import TYPE_CHECKING

import msgspec
from beancount.core.number import MISSING
from flask.json.provider import JSONProvider
from markupsafe import Markup
from msgspec import Struct

from fava.beans.abc import Transaction
from fava.beans.account import account_tester
from fava.beans.flags import FLAG_UNREALIZED
from fava.beans.helpers import slice_entry_dates
from fava.core.conversion import conversion_from_str
from fava.core.inventory import CounterInventory
from fava.core.module_base import FavaModule
from fava.util import listify

try:
    from typing import override
except ImportError:  # pragma: no cover
    from typing_extensions import override

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Mapping
    from datetime import date

    from fava.core import FilteredLedger
    from fava.core.conversion import Conversion
    from fava.core.inventory import SimpleCounterInventory
    from fava.core.tree import SerialisedTreeNode
    from fava.util.date import Interval


ZERO = Decimal()


def _enc_hook(o: object) -> object:
    """Specific serialisation for data types unknown to msgspec."""
    if isinstance(o, Pattern):
        return o.pattern
    if isinstance(o, Markup):
        return str(o)
    if o is MISSING:  # pragma: no cover
        return None
    msg = f"Unsupported type: {type(o)}"  # pragma: no cover
    raise NotImplementedError(msg)  # pragma: no cover


_encoder = msgspec.json.Encoder(enc_hook=_enc_hook, order="sorted")
_decoder = msgspec.json.Decoder()


def dumps(obj: object) -> str:
    """Dump as a JSON string."""
    return _encoder.encode(obj).decode("utf-8")


def loads(s: str | bytes) -> object:
    """Load a JSON string."""
    return _decoder.decode(s)


class FavaJSONProvider(JSONProvider):
    """Use custom JSON encoder and decoder."""

    @override
    def dumps(self, obj: object, **_kwargs: object) -> str:
        return _encoder.encode(obj).decode("utf-8")

    @override
    def loads(self, s: str | bytes, **_kwargs: object) -> object:
        return _decoder.decode(s)


class DateAndBalance(Struct, frozen=True):
    """Balance at a date."""

    date: date
    balance: SimpleCounterInventory


class DateAndBalanceWithBudget(Struct, frozen=True):
    """Balance at a date with a budget."""

    date: date
    balance: SimpleCounterInventory
    account_balances: Mapping[str, SimpleCounterInventory]
    budgets: Mapping[str, Decimal]


class ChartModule(FavaModule):
    """Return data for the various charts in Fava."""

    def hierarchy(
        self,
        filtered: FilteredLedger,
        account_name: str,
        conversion: Conversion,
    ) -> SerialisedTreeNode:
        """Render an account tree."""
        tree = filtered.root_tree
        return tree.get(account_name).serialise(
            conversion, self.ledger.prices, filtered.end_date
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
        conv = conversion_from_str(conversion)
        prices = self.ledger.prices

        # limit the bar charts to 100 intervals
        intervals = filtered.interval_ranges(interval)[-100:]

        for date_range in intervals:
            inventory = CounterInventory()
            entries = slice_entry_dates(
                filtered.entries, date_range.begin, date_range.end
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
            balance = conv.apply(
                inventory,
                prices,
                date_range.end_inclusive,
            )
            account_balances = {
                account: conv.apply(
                    acct_value,
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
        conv = conversion_from_str(conversion)

        def _balances() -> Iterable[tuple[date, CounterInventory]]:
            last_date = None
            running_balance = CounterInventory()
            is_child_account = account_tester(account_name, with_children=True)

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
            balance = conv.apply(running_bal, prices, d)
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
        conv = conversion_from_str(conversion)
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
                conv.apply(
                    inventory,
                    prices,
                    date_range.end_inclusive,
                ),
            )
