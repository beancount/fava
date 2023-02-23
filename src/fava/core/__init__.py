"""This module provides the data required by Fava's reports."""
from __future__ import annotations

import copy
import datetime
from datetime import date
from functools import lru_cache
from operator import itemgetter
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import Iterable
from typing import TYPE_CHECKING

from beancount.core import realization
from beancount.core.account_types import AccountTypes
from beancount.core.account_types import get_account_sign
from beancount.core.compare import hash_entry
from beancount.core.data import Balance
from beancount.core.data import Directive
from beancount.core.data import Entries
from beancount.core.data import iter_entry_dates
from beancount.core.data import Posting
from beancount.core.data import Price
from beancount.core.data import Transaction
from beancount.core.getters import get_min_max_dates
from beancount.core.interpolate import compute_entry_context
from beancount.core.inventory import Inventory
from beancount.core.number import Decimal
from beancount.core.prices import build_price_map
from beancount.core.prices import get_all_prices
from beancount.loader import _load  # type: ignore
from beancount.loader import load_file
from beancount.parser.options import get_account_types
from beancount.parser.options import OPTIONS_DEFAULTS
from beancount.utils.encryption import is_encrypted_file

from fava.core.accounts import AccountDict
from fava.core.accounts import get_entry_accounts
from fava.core.attributes import AttributesModule
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.commodities import CommoditiesModule
from fava.core.entries_by_type import group_entries_by_type
from fava.core.extensions import ExtensionModule
from fava.core.fava_options import FavaOptions
from fava.core.fava_options import parse_options
from fava.core.file import FileModule
from fava.core.file import get_entry_slice
from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import TimeFilter
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
from fava.util.typing import BeancountOptions

if TYPE_CHECKING:  # pragma: no cover
    from beancount.core.prices import PriceMap
    from beancount.core.realization import RealAccount


class Filters:
    """The possible entry filters."""

    __slots__ = ("account", "filter", "time")

    def __init__(
        self, options: BeancountOptions, fava_options: FavaOptions
    ) -> None:
        self.account = AccountFilter(options, fava_options)
        self.filter = AdvancedFilter(options, fava_options)
        self.time = TimeFilter(options, fava_options)

    def set(
        self,
        account: str | None = None,
        filter: str | None = None,  # pylint: disable=redefined-builtin
        time: str | None = None,
    ) -> bool:
        """Set the filters and check if one of them changed."""
        return any(
            [
                self.account.set(account),
                self.filter.set(filter),
                self.time.set(time),
            ]
        )

    def apply(self, entries: Entries) -> Entries:
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


class FilteredLedger:
    """Filtered Beancount ledger."""

    __slots__ = [
        "ledger",
        "entries",
        "filters",
        "root_account",
        "root_tree",
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
        self.filters = Filters(ledger.options, ledger.fava_options)
        self.filters.set(account=account, filter=filter, time=time)
        self.entries = self.filters.apply(ledger.all_entries)

        self.root_account = realization.realize(
            self.entries, ledger.account_types
        )
        self.root_tree = Tree(self.entries)

        self._date_first, self._date_last = get_min_max_dates(
            self.entries, (Transaction, Price)
        )
        if self._date_last:
            self._date_last = self._date_last + datetime.timedelta(1)

        if self.filters.time:
            self._date_first = self.filters.time.begin_date
            self._date_last = self.filters.time.end_date

    @property
    def end_date(self) -> date | None:
        """The date to use for prices."""
        if self.filters.time:
            return self.filters.time.end_date
        return None

    @property
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
        "account_types",
        "accounts",
        "all_entries",
        "all_entries_by_type",
        "all_root_account",
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
    all_entries: Entries

    #: A NamedTuple containing the names of the five base accounts.
    account_types: AccountTypes

    #: The price map.
    price_map: PriceMap

    #: The realized root account for all entries.
    all_root_account: RealAccount

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

        self._watcher = Watcher()

        #: List of all (unfiltered) entries.
        self.all_entries = []

        #: Dict of list of all (unfiltered) entries by type.
        self.all_entries_by_type = group_entries_by_type([])

        #: A list of all errors reported by Beancount.
        self.errors: list[BeancountError] = []

        #: A Beancount options map.
        self.options: BeancountOptions = OPTIONS_DEFAULTS

        #: A dict containing information about the accounts.
        self.accounts = AccountDict(self)

        #: A dict with all of Fava's option values.
        self.fava_options: FavaOptions = FavaOptions()

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

        self.account_types = get_account_types(self.options)
        self.price_map = build_price_map(self.all_entries)
        self.all_root_account = realization.realize(
            self.all_entries, self.account_types
        )

        self.all_entries_by_type = group_entries_by_type(self.all_entries)

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
                for account in self.account_types
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

    def get_account_sign(self, account_name: str) -> int:
        """Get account sign.

        Arguments:
            account_name: An account name.

        Returns:
            The sign of the given account, +1 for an assets or expenses
            account, -1 otherwise.
        """
        return get_account_sign(account_name, self.account_types)

    def interval_balances(
        self,
        filtered: FilteredLedger,
        interval: Interval,
        account_name: str,
        accumulate: bool = False,
    ) -> tuple[list[realization.RealAccount], list[tuple[date, date]]]:
        """Balances by interval.

        Arguments:
            filtered: The currently filtered ledger.
            interval: An interval.
            account_name: An account name.
            accumulate: A boolean, ``True`` if the balances for an interval
                should include all entries up to the end of the interval.

        Returns:
            A list of RealAccount instances for all the intervals.
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
            realization.realize(
                list(
                    iter_entry_dates(
                        filtered.entries,
                        date.min if accumulate else begin_date,
                        end_date,
                    )
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
    ) -> list[tuple[Directive, list[Posting], Inventory, Inventory]]:
        """Journal for an account.

        Args:
            filtered: The currently filtered ledger.
            account_name: An account name.
            with_journal_children: Whether to include postings of subaccounts
                of the given account.

        Returns:
            A list of tuples ``(entry, postings, change, balance)``.
            change and balance have already been reduced to units.
        """
        real_account = realization.get_or_create(
            filtered.root_account, account_name
        )

        if with_journal_children:
            postings = realization.get_postings(real_account)
        else:
            postings = real_account.txn_postings

        return [
            (entry, postings_, copy.copy(change), copy.copy(balance))
            for (
                entry,
                postings_,
                change,
                balance,
            ) in realization.iterate_with_balance(postings)
        ]

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

        balances = compute_entry_context(self.all_entries, entry)
        before = {
            acc: [pos.to_string() for pos in sorted(inv)]
            for acc, inv in balances[0].items()
        }
        after = {
            acc: [pos.to_string() for pos in sorted(inv)]
            for acc, inv in balances[1].items()
        }
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

    @staticmethod
    def group_entries_by_type(entries: Entries) -> list[tuple[str, Entries]]:
        """Group the given entries by type.

        Args:
            entries: The entries to group.

        Returns:
            A list of tuples (type, entries) consisting of the directive type
            as a string and the list of corresponding entries.
        """
        groups: dict[str, Entries] = {}
        for entry in entries:
            groups.setdefault(entry.__class__.__name__, []).append(entry)

        return sorted(groups.items(), key=itemgetter(0))
