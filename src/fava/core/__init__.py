"""This module provides the data required by Fava's reports."""
from __future__ import annotations

import datetime
from datetime import date
from decimal import Decimal
from functools import lru_cache
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import Callable
from typing import Iterable
from typing import TYPE_CHECKING
from typing import TypeVar

from beancount.core import realization
from beancount.core.data import iter_entry_dates
from beancount.core.getters import get_min_max_dates
from beancount.core.inventory import Inventory
from beancount.core.prices import build_price_map
from beancount.core.prices import get_all_prices
from beancount.core.realization import RealAccount
from beancount.loader import _load  # type: ignore
from beancount.loader import load_file
from beancount.utils.encryption import is_encrypted_file

from fava.beans.abc import Balance
from fava.beans.abc import Directive
from fava.beans.abc import Price
from fava.beans.abc import Transaction
from fava.beans.account import get_entry_accounts
from fava.beans.funcs import hash_entry
from fava.beans.str import to_string
from fava.beans.types import BeancountOptions
from fava.core.accounts import AccountDict
from fava.core.attributes import AttributesModule
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.commodities import CommoditiesModule
from fava.core.extensions import ExtensionModule
from fava.core.fava_options import FavaOptions
from fava.core.fava_options import parse_options
from fava.core.file import FileModule
from fava.core.file import get_entry_slice
from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import TimeFilter
from fava.core.group_entries import EntriesByType
from fava.core.group_entries import group_entries_by_type
from fava.core.ingest import IngestModule
from fava.core.misc import FavaMisc
from fava.core.number import DecimalFormatModule
from fava.core.query_shell import QueryShell
from fava.core.tree import Tree
from fava.core.watcher import Watcher
from fava.helpers import BeancountError
from fava.helpers import FavaAPIException
from fava.util import pairwise
from fava.util.date import Interval
from fava.util.date import interval_ends

if TYPE_CHECKING:  # pragma: no cover
    from beancount.core.prices import PriceMap


class Filters:
    """The possible entry filters."""

    __slots__ = ("account", "filter", "time")

    def __init__(
        self,
        options: BeancountOptions,
        fava_options: FavaOptions,
        account: str | None = None,
        filter: str | None = None,  # pylint: disable=redefined-builtin
        time: str | None = None,
    ) -> None:
        self.account = AccountFilter(options, fava_options)
        self.filter = AdvancedFilter(options, fava_options)
        self.time = TimeFilter(options, fava_options)
        self.account.set(account)
        self.filter.set(filter)
        self.time.set(time)

    def apply(self, entries: list[Directive]) -> list[Directive]:
        """Apply the filters to the entries."""
        entries = self.account.apply(entries)
        entries = self.filter.apply(entries)
        entries = self.time.apply(entries)
        return entries


MODULES = [
    "accounts",
    "attributes",
    "budgets",
    "charts",
    "commodities",
    "extensions",
    "file",
    "format_decimal",
    "misc",
    "query_shell",
    "ingest",
]

T = TypeVar("T")


def _cache(func: Callable[..., T]) -> T:
    """Wrap lru_cache to avoid type errors."""
    # With Python 3.8 the calls below could be replaced with cached_property
    return lru_cache()(func)  # type: ignore


class FilteredLedger:
    """Filtered Beancount ledger."""

    __slots__ = [
        "ledger",
        "entries",
        "filters",
        "_date_first",
        "_date_last",
    ]
    _date_first: date | None
    _date_last: date | None

    def __init__(
        self,
        ledger: FavaLedger,
        account: str | None = None,
        filter: str | None = None,  # pylint: disable=redefined-builtin
        time: str | None = None,
    ):
        self.ledger = ledger
        self.filters = Filters(
            ledger.options,
            ledger.fava_options,
            account=account,
            filter=filter,
            time=time,
        )
        self.entries = self.filters.apply(ledger.all_entries)

        self._date_first, self._date_last = get_min_max_dates(
            self.entries, (Transaction, Price)
        )
        if self._date_last:
            self._date_last = self._date_last + datetime.timedelta(1)

        if self.filters.time:
            self._date_first = self.filters.time.begin_date
            self._date_last = self.filters.time.end_date

    @property
    @_cache
    def root_account(self) -> RealAccount:
        """A realized account for the filtered entries."""
        return realization.realize(
            self.entries, self.ledger.root_accounts  # type: ignore
        )

    @property
    def end_date(self) -> date | None:
        """The date to use for prices."""
        if self.filters.time:
            return self.filters.time.end_date
        return None

    @property
    @_cache
    def root_tree(self) -> Tree:
        """A root tree."""
        return Tree(self.entries)

    @property
    @_cache
    def root_tree_closed(self) -> Tree:
        """A root tree for the balance sheet."""
        tree = Tree(self.entries)
        tree.cap(self.ledger.options, self.ledger.fava_options.unrealized)
        return tree

    def interval_ends(self, interval: Interval) -> Iterable[date]:
        """Yield dates corresponding to interval boundaries."""
        if not self._date_first or not self._date_last:
            return []
        return interval_ends(self._date_first, self._date_last, interval)

    def prices(self, base: str, quote: str) -> list[tuple[date, Decimal]]:
        """List all prices."""
        all_prices = get_all_prices(self.ledger.price_map, (base, quote))

        if (
            self.filters.time
            and self.filters.time.begin_date is not None
            and self.filters.time.end_date is not None
        ):
            return [
                (date_, price)
                for date_, price in all_prices
                if self.filters.time.begin_date
                <= date_
                < self.filters.time.end_date
            ]
        return all_prices

    def account_is_closed(self, account_name: str) -> bool:
        """Check if the account is closed.

        Args:
            account_name: An account name.

        Returns:
            True if the account is closed before the end date of the current
            time filter.
        """
        if self.filters.time and self._date_last is not None:
            return (
                self.ledger.accounts[account_name].close_date < self._date_last
            )
        return self.ledger.accounts[account_name].close_date != date.max


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class FavaLedger:
    """Create an interface for a Beancount ledger.

    Arguments:
        path: Path to the main Beancount file.
    """

    __slots__ = [
        "accounts",
        "all_entries",
        "all_entries_by_type",
        "beancount_file_path",
        "errors",
        "fava_options",
        "_is_encrypted",
        "options",
        "price_map",
        "_watcher",
        *MODULES,
    ]

    #: List of all (unfiltered) entries.
    all_entries: list[Directive]

    #: A list of all errors reported by Beancount.
    errors: list[BeancountError]

    #: The Beancount options map.
    options: BeancountOptions

    #: A dict with all of Fava's option values.
    fava_options: FavaOptions

    #: The price map.
    price_map: PriceMap

    #: Dict of list of all (unfiltered) entries by type.
    all_entries_by_type: EntriesByType

    def __init__(self, path: str) -> None:
        #: The path to the main Beancount file.
        self.beancount_file_path = path
        self._is_encrypted = is_encrypted_file(path)

        #: An :class:`AttributesModule` instance.
        self.attributes = AttributesModule(self)

        #: A :class:`.BudgetModule` instance.
        self.budgets = BudgetModule(self)

        #: A :class:`.ChartModule` instance.
        self.charts = ChartModule(self)

        #: A :class:`.CommoditiesModule` instance.
        self.commodities = CommoditiesModule(self)

        #: A :class:`.ExtensionModule` instance.
        self.extensions = ExtensionModule(self)

        #: A :class:`.FileModule` instance.
        self.file = FileModule(self)

        #: A :class:`.IngestModule` instance.
        self.ingest = IngestModule(self)

        #: A :class:`.FavaMisc` instance.
        self.misc = FavaMisc(self)

        #: A :class:`.DecimalFormatModule` instance.
        self.format_decimal = DecimalFormatModule(self)

        #: A :class:`.QueryShell` instance.
        self.query_shell = QueryShell(self)

        #: A :class:`.AccountDict` module - a dict with information about the accounts.
        self.accounts = AccountDict(self)

        self._watcher = Watcher()

        self.load_file()

    def load_file(self) -> None:
        """Load the main file and all included files and set attributes."""
        # use the internal function to disable cache
        if not self._is_encrypted:
            # pylint: disable=protected-access
            self.all_entries, self.errors, self.options = _load(
                [(self.beancount_file_path, True)], None, None, None
            )
        else:
            self.all_entries, self.errors, self.options = load_file(
                self.beancount_file_path
            )

        self.get_filtered.cache_clear()

        self.all_entries_by_type = group_entries_by_type(self.all_entries)
        self.price_map = build_price_map(self.all_entries_by_type.Price)  # type: ignore

        self.fava_options, errors = parse_options(
            self.all_entries_by_type.Custom
        )
        self.errors.extend(errors)

        if not self._is_encrypted:
            self._watcher.update(*self.paths_to_watch())

        for mod in MODULES:
            getattr(self, mod).load_file()

    @lru_cache(maxsize=16)  # noqa: B019
    def get_filtered(
        self,
        account: str | None = None,
        filter: str | None = None,  # pylint: disable=redefined-builtin
        time: str | None = None,
    ) -> FilteredLedger:
        """Filter the ledger."""
        return FilteredLedger(
            ledger=self, account=account, filter=filter, time=time
        )

    @property
    def mtime(self) -> int:
        """The timestamp to the latest change of the underlying files."""
        return self._watcher.last_checked

    @property
    def root_accounts(self) -> tuple[str, str, str, str, str]:
        """The five root accounts."""
        options = self.options
        return (
            options["name_assets"],
            options["name_liabilities"],
            options["name_equity"],
            options["name_income"],
            options["name_expenses"],
        )

    def join_path(self, *args: str) -> str:
        """Path relative to the directory of the ledger."""
        include_path = dirname(self.beancount_file_path)
        return normpath(join(include_path, *args))

    def paths_to_watch(self) -> tuple[list[str], list[str]]:
        """Get paths to included files and document directories.

        Returns:
            A tuple (files, directories).
        """
        files = list(self.options["include"])
        if self.ingest.module_path:
            files.append(self.ingest.module_path)
        return (
            files,
            [
                self.join_path(path, account)
                for account in self.root_accounts
                for path in self.options["documents"]
            ],
        )

    def changed(self) -> bool:
        """Check if the file needs to be reloaded.

        Returns:
            True if a change in one of the included files or a change in a
            document folder was detected and the file has been reloaded.
        """
        # We can't reload an encrypted file, so act like it never changes.
        if self._is_encrypted:
            return False
        changed = self._watcher.check()
        if changed:
            self.load_file()
        return changed

    def interval_balances(
        self,
        filtered: FilteredLedger,
        interval: Interval,
        account_name: str,
        accumulate: bool = False,
    ) -> tuple[list[Tree], list[tuple[date, date]]]:
        """Balances by interval.

        Arguments:
            filtered: The currently filtered ledger.
            interval: An interval.
            account_name: An account name.
            accumulate: A boolean, ``True`` if the balances for an interval
                should include all entries up to the end of the interval.

        Returns:
            A pair of a list of Tree instances and the intervals.
        """
        min_accounts = [
            account
            for account in self.accounts.keys()
            if account.startswith(account_name)
        ]

        interval_tuples = list(
            reversed(list(pairwise(filtered.interval_ends(interval))))
        )

        interval_balances = [
            Tree(
                iter_entry_dates(
                    filtered.entries,
                    date.min if accumulate else begin_date,
                    end_date,
                ),
                min_accounts,
            )
            for begin_date, end_date in interval_tuples
        ]

        return interval_balances, interval_tuples

    def account_journal(
        self,
        filtered: FilteredLedger,
        account_name: str,
        with_journal_children: bool = False,
    ) -> Iterable[tuple[Directive, Inventory, Inventory]]:
        """Journal for an account.

        Args:
            filtered: The currently filtered ledger.
            account_name: An account name.
            with_journal_children: Whether to include postings of subaccounts
                of the given account.

        Returns:
            A generator of ``(entry, change, balance)`` tuples.
            change and balance have already been reduced to units.
        """
        real_account = realization.get_or_create(
            filtered.root_account, account_name
        )
        txn_postings = (
            realization.get_postings(real_account)
            if with_journal_children
            else real_account.txn_postings
        )

        return (
            (entry, change, balance)
            for (
                entry,
                _postings,
                change,
                balance,
            ) in realization.iterate_with_balance(
                txn_postings  # type: ignore
            )
        )

    def get_entry(self, entry_hash: str) -> Directive:
        """Find an entry.

        Arguments:
            entry_hash: Hash of the entry.

        Returns:
            The entry with the given hash.
        Raises:
            FavaAPIException: If there is no entry for the given hash.
        """
        try:
            return next(
                entry
                for entry in self.all_entries
                if entry_hash == hash_entry(entry)
            )
        except StopIteration as exc:
            raise FavaAPIException(
                f'No entry found for hash "{entry_hash}"'
            ) from exc

    def context(
        self, entry_hash: str
    ) -> tuple[
        Directive,
        dict[str, list[str]] | None,
        dict[str, list[str]] | None,
        str,
        str,
    ]:
        """Context for an entry.

        Arguments:
            entry_hash: Hash of entry.

        Returns:
            A tuple ``(entry, before, after, source_slice, sha256sum)`` of the
            (unique) entry with the given ``entry_hash``. If the entry is a
            Balance or Transaction then ``before`` and ``after`` contain
            the balances before and after the entry of the affected accounts.
        """
        entry = self.get_entry(entry_hash)
        source_slice, sha256sum = get_entry_slice(entry)

        if not isinstance(entry, (Balance, Transaction)):
            return entry, None, None, source_slice, sha256sum

        entry_accounts = get_entry_accounts(entry)
        balances = {account: Inventory() for account in entry_accounts}
        for entry_ in self.all_entries:
            if entry_ is entry:
                break
            if isinstance(entry_, Transaction):
                for posting in entry_.postings:
                    balance = balances.get(posting.account, None)
                    if balance is not None:
                        balance.add_position(posting)

        def visualise(inv: Inventory) -> list[str]:
            return [to_string(pos) for pos in sorted(inv)]

        before = {acc: visualise(inv) for acc, inv in balances.items()}

        if isinstance(entry, Balance):
            return entry, before, None, source_slice, sha256sum

        for posting in entry.postings:
            balances[posting.account].add_position(posting)
        after = {acc: visualise(inv) for acc, inv in balances.items()}
        return entry, before, after, source_slice, sha256sum

    def commodity_pairs(self) -> list[tuple[str, str]]:
        """List pairs of commodities.

        Returns:
            A list of pairs of commodities. Pairs of operating currencies will
            be given in both directions not just in the one found in file.
        """
        fw_pairs = self.price_map.forward_pairs
        bw_pairs = []
        for currency_a, currency_b in fw_pairs:
            if (
                currency_a in self.options["operating_currency"]
                and currency_b in self.options["operating_currency"]
            ):
                bw_pairs.append((currency_b, currency_a))
        return sorted(fw_pairs + bw_pairs)

    def statement_path(self, entry_hash: str, metadata_key: str) -> str:
        """Get the path for a statement found in the specified entry."""
        entry = self.get_entry(entry_hash)
        value = entry.meta[metadata_key]

        accounts = set(get_entry_accounts(entry))
        full_path = join(dirname(entry.meta["filename"]), value)
        for document in self.all_entries_by_type.Document:
            if document.filename == full_path:
                return document.filename
            if document.account in accounts:
                if basename(document.filename) == value:
                    return document.filename

        raise FavaAPIException("Statement not found.")

    group_entries_by_type = staticmethod(group_entries_by_type)
