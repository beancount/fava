"""This module provides the data required by Fava's reports."""

from __future__ import annotations

from datetime import date
from datetime import timedelta
from functools import cached_property
from functools import lru_cache
from itertools import takewhile
from pathlib import Path
from typing import TYPE_CHECKING

from beancount.core.data import iter_entry_dates
from beancount.core.inventory import Inventory
from beancount.utils.encryption import is_encrypted_file

from fava.beans.abc import Balance
from fava.beans.abc import Price
from fava.beans.abc import Transaction
from fava.beans.account import account_tester
from fava.beans.account import get_entry_accounts
from fava.beans.funcs import get_position
from fava.beans.funcs import hash_entry
from fava.beans.load import load_uncached
from fava.beans.prices import FavaPriceMap
from fava.beans.str import to_string
from fava.core.accounts import AccountDict
from fava.core.attributes import AttributesModule
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.commodities import CommoditiesModule
from fava.core.conversion import cost_or_value
from fava.core.extensions import ExtensionModule
from fava.core.fava_options import parse_options
from fava.core.file import FileModule
from fava.core.file import get_entry_slice
from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import TimeFilter
from fava.core.group_entries import group_entries_by_type
from fava.core.ingest import IngestModule
from fava.core.inventory import CounterInventory
from fava.core.misc import FavaMisc
from fava.core.number import DecimalFormatModule
from fava.core.query_shell import QueryShell
from fava.core.tree import Tree
from fava.core.watcher import Watcher
from fava.core.watcher import WatchfilesWatcher
from fava.helpers import FavaAPIError
from fava.util import listify
from fava.util.date import dateranges

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence
    from decimal import Decimal

    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions
    from fava.core.conversion import Conversion
    from fava.core.fava_options import FavaOptions
    from fava.core.group_entries import EntriesByType
    from fava.core.inventory import SimpleCounterInventory
    from fava.helpers import BeancountError
    from fava.util.date import DateRange
    from fava.util.date import Interval


class EntryNotFoundForHashError(FavaAPIError):
    """Entry not found for hash."""

    def __init__(self, entry_hash: str) -> None:
        super().__init__(f'No entry found for hash "{entry_hash}"')


class StatementNotFoundError(FavaAPIError):
    """Statement not found."""

    def __init__(self) -> None:
        super().__init__("Statement not found.")


class StatementMetadataInvalidError(FavaAPIError):
    """Statement metadata not found or invalid."""

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Statement path at key '{key}' missing or not a string."
        )


class FilteredLedger:
    """Filtered Beancount ledger."""

    __slots__ = (
        "__dict__",  # for the cached_property decorator
        "_date_first",
        "_date_last",
        "date_range",
        "entries",
        "ledger",
    )
    _date_first: date | None
    _date_last: date | None

    def __init__(
        self,
        ledger: FavaLedger,
        *,
        account: str | None = None,
        filter: str | None = None,  # noqa: A002
        time: str | None = None,
    ) -> None:
        self.ledger = ledger
        self.date_range: DateRange | None = None

        entries = ledger.all_entries
        if account:
            entries = AccountFilter(account).apply(entries)
        if filter and filter.strip():
            entries = AdvancedFilter(filter.strip()).apply(entries)
        if time:
            time_filter = TimeFilter(ledger.options, ledger.fava_options, time)
            entries = time_filter.apply(entries)
            self.date_range = time_filter.date_range
        self.entries = entries

        if self.date_range:
            self._date_first = self.date_range.begin
            self._date_last = self.date_range.end
            return

        self._date_first = None
        self._date_last = None
        for entry in self.entries:
            if isinstance(entry, Transaction):
                self._date_first = entry.date
                break
        for entry in reversed(self.entries):
            if isinstance(entry, (Transaction, Price)):
                self._date_last = entry.date + timedelta(1)
                break

    @property
    def end_date(self) -> date | None:
        """The date to use for prices."""
        date_range = self.date_range
        if date_range:
            return date_range.end_inclusive
        return None

    @cached_property
    def root_tree(self) -> Tree:
        """A root tree."""
        return Tree(self.entries)

    @cached_property
    def root_tree_closed(self) -> Tree:
        """A root tree for the balance sheet."""
        tree = Tree(self.entries)
        tree.cap(self.ledger.options, self.ledger.fava_options.unrealized)
        return tree

    @listify
    def interval_ranges(self, interval: Interval) -> Iterable[DateRange]:
        """Yield date ranges corresponding to interval boundaries."""
        if not self._date_first or not self._date_last:
            return []
        return dateranges(self._date_first, self._date_last, interval)

    def prices(self, base: str, quote: str) -> Sequence[tuple[date, Decimal]]:
        """List all prices."""
        all_prices = self.ledger.prices.get_all_prices((base, quote))
        if all_prices is None:
            return []

        date_range = self.date_range
        if date_range:
            return [
                price_point
                for price_point in all_prices
                if date_range.begin <= price_point[0] < date_range.end
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
        date_range = self.date_range
        close_date = self.ledger.accounts[account_name].close_date
        if close_date is None:
            return False
        return close_date < date_range.end if date_range else True


class FavaLedger:
    """Create an interface for a Beancount ledger.

    Arguments:
        path: Path to the main Beancount file.
    """

    __slots__ = (
        "_is_encrypted",
        "accounts",
        "accounts",
        "all_entries",
        "all_entries_by_type",
        "attributes",
        "beancount_file_path",
        "budgets",
        "charts",
        "commodities",
        "extensions",
        "fava_options",
        "fava_options_errors",
        "file",
        "format_decimal",
        "get_filtered",
        "ingest",
        "load_errors",
        "misc",
        "options",
        "prices",
        "query_shell",
        "watcher",
    )

    #: List of all (unfiltered) entries.
    all_entries: Sequence[Directive]

    #: A list of all errors reported by Beancount.
    load_errors: Sequence[BeancountError]

    #: The Beancount options map.
    options: BeancountOptions

    #: A dict with all of Fava's option values.
    fava_options: FavaOptions

    #: A list of all errors from parsing the custom options.
    fava_options_errors: Sequence[BeancountError]

    #: The price map.
    prices: FavaPriceMap

    #: Dict of list of all (unfiltered) entries by type.
    all_entries_by_type: EntriesByType

    def __init__(self, path: str, *, poll_watcher: bool = False) -> None:
        #: The path to the main Beancount file.
        self.beancount_file_path = path
        self._is_encrypted = is_encrypted_file(path)
        self.get_filtered = lru_cache(maxsize=16)(self._get_filtered)

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

        #: A :class:`.AccountDict` module - details about the accounts.
        self.accounts = AccountDict(self)

        self.watcher = WatchfilesWatcher() if not poll_watcher else Watcher()

        self.load_file()

    def load_file(self) -> None:
        """Load the main file and all included files and set attributes."""
        self.all_entries, self.load_errors, self.options = load_uncached(
            self.beancount_file_path,
            is_encrypted=self._is_encrypted,
        )
        self.get_filtered.cache_clear()

        self.all_entries_by_type = group_entries_by_type(self.all_entries)
        self.prices = FavaPriceMap(self.all_entries_by_type.Price)

        self.fava_options, self.fava_options_errors = parse_options(
            self.all_entries_by_type.Custom,
        )

        if self._is_encrypted:  # pragma: no cover
            pass
        else:
            self.watcher.update(*self.paths_to_watch())

        # Call load_file of all modules.
        self.accounts.load_file()
        self.attributes.load_file()
        self.budgets.load_file()
        self.charts.load_file()
        self.commodities.load_file()
        self.extensions.load_file()
        self.file.load_file()
        self.format_decimal.load_file()
        self.misc.load_file()
        self.query_shell.load_file()
        self.ingest.load_file()

        self.extensions.after_load_file()

    def _get_filtered(
        self,
        account: str | None = None,
        filter: str | None = None,  # noqa: A002
        time: str | None = None,
    ) -> FilteredLedger:
        """Filter the ledger."""
        return FilteredLedger(
            ledger=self,
            account=account,
            filter=filter,
            time=time,
        )

    @property
    def mtime(self) -> int:
        """The timestamp to the latest change of the underlying files."""
        return self.watcher.last_checked

    @property
    def errors(self) -> Sequence[BeancountError]:
        """The errors that the Beancount loading plus Fava module errors."""
        return [
            *self.load_errors,
            *self.fava_options_errors,
            *self.budgets.errors,
            *self.extensions.errors,
            *self.misc.errors,
            *self.ingest.errors,
        ]

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

    def join_path(self, *args: str) -> Path:
        """Path relative to the directory of the ledger."""
        return Path(self.beancount_file_path).parent.joinpath(*args).resolve()

    def paths_to_watch(self) -> tuple[Sequence[Path], Sequence[Path]]:
        """Get paths to included files and document directories.

        Returns:
            A tuple (files, directories).
        """
        files = [Path(i) for i in self.options["include"]]
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
        if self._is_encrypted:  # pragma: no cover
            return False
        changed = self.watcher.check()
        if changed:
            self.load_file()
        return changed

    def interval_balances(
        self,
        filtered: FilteredLedger,
        interval: Interval,
        account_name: str,
        *,
        accumulate: bool = False,
    ) -> tuple[Sequence[Tree], Sequence[DateRange]]:
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
            for account in self.accounts
            if account.startswith(account_name)
        ]

        interval_ranges = list(reversed(filtered.interval_ranges(interval)))
        interval_balances = [
            Tree(
                iter_entry_dates(
                    filtered.entries,
                    date.min if accumulate else date_range.begin,
                    date_range.end,
                ),
                min_accounts,
            )
            for date_range in interval_ranges
        ]

        return interval_balances, interval_ranges

    @listify
    def account_journal(
        self,
        filtered: FilteredLedger,
        account_name: str,
        conversion: str | Conversion,
        *,
        with_children: bool,
    ) -> Iterable[
        tuple[Directive, SimpleCounterInventory, SimpleCounterInventory]
    ]:
        """Journal for an account.

        Args:
            filtered: The currently filtered ledger.
            account_name: An account name.
            conversion: The conversion to use.
            with_children: Whether to include postings of subaccounts of
                           the account.

        Yields:
            Tuples of ``(entry, change, balance)``.
        """
        relevant_account = account_tester(
            account_name, with_children=with_children
        )

        prices = self.prices
        balance = CounterInventory()
        for entry in filtered.entries:
            change = CounterInventory()
            entry_is_relevant = False
            postings = getattr(entry, "postings", None)
            if postings is not None:
                for posting in postings:
                    if relevant_account(posting.account):
                        entry_is_relevant = True
                        balance.add_position(posting)
                        change.add_position(posting)
            elif any(relevant_account(a) for a in get_entry_accounts(entry)):
                entry_is_relevant = True

            if entry_is_relevant:
                yield (
                    entry,
                    cost_or_value(change, conversion, prices, entry.date),
                    cost_or_value(balance, conversion, prices, entry.date),
                )

    def get_entry(self, entry_hash: str) -> Directive:
        """Find an entry.

        Arguments:
            entry_hash: Hash of the entry.

        Returns:
            The entry with the given hash.

        Raises:
            EntryNotFoundForHashError: If there is no entry for the given hash.
        """
        try:
            return next(
                entry
                for entry in self.all_entries
                if entry_hash == hash_entry(entry)
            )
        except StopIteration as exc:
            raise EntryNotFoundForHashError(entry_hash) from exc

    def context(
        self,
        entry_hash: str,
    ) -> tuple[
        Directive,
        Mapping[str, Sequence[str]] | None,
        Mapping[str, Sequence[str]] | None,
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
        for entry_ in takewhile(lambda e: e is not entry, self.all_entries):
            if isinstance(entry_, Transaction):
                for posting in entry_.postings:
                    balance = balances.get(posting.account, None)
                    if balance is not None:
                        balance.add_position(posting)

        def visualise(inv: Inventory) -> Sequence[str]:
            return [to_string(pos) for pos in sorted(inv)]

        before = {acc: visualise(inv) for acc, inv in balances.items()}

        if isinstance(entry, Balance):
            return entry, before, None, source_slice, sha256sum

        for posting in entry.postings:
            balances[posting.account].add_position(posting)
        after = {acc: visualise(inv) for acc, inv in balances.items()}
        return entry, before, after, source_slice, sha256sum

    def commodity_pairs(self) -> Sequence[tuple[str, str]]:
        """List pairs of commodities.

        Returns:
            A list of pairs of commodities. Pairs of operating currencies will
            be given in both directions not just in the one found in file.
        """
        return self.prices.commodity_pairs(self.options["operating_currency"])

    def statement_path(self, entry_hash: str, metadata_key: str) -> str:
        """Get the path for a statement found in the specified entry.

        The entry that we look up should contain a path to a document (absolute
        or relative to the filename of the entry) or just its basename. We go
        through all documents and match on the full path or if one of the
        documents with a matching account has a matching file basename.

        Arguments:
            entry_hash: Hash of the entry containing the path in its metadata.
            metadata_key: The key that the path should be in.

        Returns:
            The filename of the matching document entry.

        Raises:
            StatementMetadataInvalidError: If the metadata at the given key is
                                           invalid.
            StatementNotFoundError: If no matching document is found.
        """
        entry = self.get_entry(entry_hash)
        value = entry.meta.get(metadata_key, None)
        if not isinstance(value, str):
            raise StatementMetadataInvalidError(metadata_key)

        accounts = set(get_entry_accounts(entry))
        filename, _ = get_position(entry)
        full_path = Path(filename).parent / value
        for document in self.all_entries_by_type.Document:
            document_path = Path(document.filename)
            if document_path == full_path:
                return document.filename
            if document.account in accounts and document_path.name == value:
                return document.filename

        raise StatementNotFoundError

    group_entries_by_type = staticmethod(group_entries_by_type)
