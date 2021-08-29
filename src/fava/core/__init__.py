"""This module provides the data required by Fava's reports."""
import copy
import datetime
from operator import itemgetter
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import normpath
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from beancount import loader  # type: ignore
from beancount.core import realization
from beancount.core.account_types import AccountTypes
from beancount.core.account_types import get_account_sign
from beancount.core.compare import hash_entry
from beancount.core.data import Balance
from beancount.core.data import Close
from beancount.core.data import Commodity
from beancount.core.data import Directive
from beancount.core.data import Document
from beancount.core.data import Entries
from beancount.core.data import Event
from beancount.core.data import get_entry
from beancount.core.data import iter_entry_dates
from beancount.core.data import Posting
from beancount.core.data import Price
from beancount.core.data import Transaction
from beancount.core.data import TxnPosting
from beancount.core.getters import get_min_max_dates
from beancount.core.interpolate import compute_entry_context
from beancount.core.inventory import Inventory
from beancount.core.number import Decimal
from beancount.core.prices import build_price_map
from beancount.core.prices import get_all_prices
from beancount.parser.options import get_account_types
from beancount.parser.options import OPTIONS_DEFAULTS
from beancount.utils.encryption import is_encrypted_file  # type: ignore

from fava.core._compat import FLAG_UNREALIZED
from fava.core.accounts import AccountDict
from fava.core.accounts import get_entry_accounts
from fava.core.attributes import AttributesModule
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.entries_by_type import group_entries_by_type
from fava.core.extensions import ExtensionModule
from fava.core.fava_options import DEFAULTS
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
from fava.util import date
from fava.util import pairwise
from fava.util.typing import BeancountOptions


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
        account: Optional[str] = None,
        filter: Optional[str] = None,  # pylint: disable=redefined-builtin
        time: Optional[str] = None,
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
    "attributes",
    "budgets",
    "charts",
    "extensions",
    "file",
    "format_decimal",
    "misc",
    "query_shell",
    "ingest",
]


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
        "commodities",
        "_date_first",
        "_date_last",
        "entries",
        "errors",
        "fava_options",
        "filters",
        "_is_encrypted",
        "options",
        "price_map",
        "root_account",
        "root_tree",
        "_watcher",
    ] + MODULES

    #: List of all (unfiltered) entries.
    all_entries: Entries

    #: The entries filtered according to the chosen filters.
    entries: Entries

    #: A NamedTuple containing the names of the five base accounts.
    account_types: AccountTypes

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
        self.errors: List[BeancountError] = []

        #: A Beancount options map.
        self.options: BeancountOptions = OPTIONS_DEFAULTS

        #: A dict containing information about the accounts.
        self.accounts = AccountDict()

        #: A dict containing information about the commodities
        self.commodities: Dict[str, Commodity] = {}

        #: A dict with all of Fava's option values.
        self.fava_options: FavaOptions = DEFAULTS

        self._date_first: Optional[datetime.date] = None
        self._date_last: Optional[datetime.date] = None

        self.load_file()

    def load_file(self) -> None:
        """Load the main file and all included files and set attributes."""
        # use the internal function to disable cache
        if not self._is_encrypted:
            # pylint: disable=protected-access
            self.all_entries, self.errors, self.options = loader._load(
                [(self.beancount_file_path, True)], None, None, None
            )
        else:
            self.all_entries, self.errors, self.options = loader.load_file(
                self.beancount_file_path
            )

        self.account_types = get_account_types(self.options)
        self.price_map = build_price_map(self.all_entries)
        self.all_root_account = realization.realize(
            self.all_entries, self.account_types
        )

        self.all_entries_by_type = group_entries_by_type(self.all_entries)

        self.accounts = AccountDict()
        for open_entry in self.all_entries_by_type.Open:
            self.accounts.setdefault(open_entry.account).meta = open_entry.meta
        for close in self.all_entries_by_type.Close:
            self.accounts.setdefault(close.account).close_date = close.date

        self.commodities = {}
        for commodity in self.all_entries_by_type.Commodity:
            self.commodities[commodity.currency] = commodity

        self.fava_options, errors = parse_options(
            self.all_entries_by_type.Custom
        )
        self.errors.extend(errors)

        if not self._is_encrypted:
            self._watcher.update(*self.paths_to_watch())

        for mod in MODULES:
            getattr(self, mod).load_file()

        self.filters = Filters(self.options, self.fava_options)

        self.filter(True)

    # pylint: disable=attribute-defined-outside-init
    def filter(
        self,
        force: bool = False,
        account: Optional[str] = None,
        filter: Optional[str] = None,  # pylint: disable=redefined-builtin
        time: Optional[str] = None,
    ) -> None:
        """Set and apply (if necessary) filters."""
        changed = self.filters.set(account=account, filter=filter, time=time)

        if not (changed or force):
            return

        self.entries = self.filters.apply(self.all_entries)

        self.root_account = realization.realize(
            self.entries, self.account_types
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
    def end_date(self) -> Optional[datetime.date]:
        """The date to use for prices."""
        if self.filters.time:
            return self.filters.time.end_date
        return None

    def join_path(self, *args: str) -> str:
        """Path relative to the directory of the ledger."""
        include_path = dirname(self.beancount_file_path)
        return normpath(join(include_path, *args))

    def paths_to_watch(self) -> Tuple[List[str], List[str]]:
        """The paths to included files and document directories.

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

    def interval_ends(
        self, interval: date.Interval
    ) -> Iterable[datetime.date]:
        """Generator yielding dates corresponding to interval boundaries."""
        if not self._date_first or not self._date_last:
            return []
        return date.interval_ends(self._date_first, self._date_last, interval)

    def get_account_sign(self, account_name: str) -> int:
        """Get account sign.

        Arguments:
            account_name: An account name.

        Returns:
            The sign of the given account, +1 for an assets or expenses
            account, -1 otherwise.
        """
        return get_account_sign(account_name, self.account_types)

    @property
    def root_tree_closed(self) -> Tree:
        """A root tree for the balance sheet."""
        tree = Tree(self.entries)
        tree.cap(self.options, self.fava_options["unrealized"])
        return tree

    def interval_balances(
        self,
        interval: date.Interval,
        account_name: str,
        accumulate: bool = False,
    ) -> Tuple[
        List[realization.RealAccount],
        List[Tuple[datetime.date, datetime.date]],
    ]:
        """Balances by interval.

        Arguments:
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
            reversed(list(pairwise(self.interval_ends(interval))))
        )

        interval_balances = [
            realization.realize(
                list(
                    iter_entry_dates(
                        self.entries,
                        datetime.date.min if accumulate else begin_date,
                        end_date,
                    )
                ),
                min_accounts,
            )
            for begin_date, end_date in interval_tuples
        ]

        return interval_balances, interval_tuples

    def account_journal(
        self, account_name: str, with_journal_children: bool = False
    ) -> List[Tuple[Directive, List[Posting], Inventory, Inventory]]:
        """Journal for an account.

        Args:
            account_name: An account name.
            with_journal_children: Whether to include postings of subaccounts
                of the given account.

        Returns:
            A list of tuples ``(entry, postings, change, balance)``.
            change and balance have already been reduced to units.
        """
        real_account = realization.get_or_create(
            self.root_account, account_name
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

    @property
    def documents(self) -> List[Document]:
        """All currently filtered documents."""
        return [e for e in self.entries if isinstance(e, Document)]

    def events(self, event_type: Optional[str] = None) -> List[Event]:
        """List events (possibly filtered by type)."""
        events = [e for e in self.entries if isinstance(e, Event)]
        if event_type:
            return [event for event in events if event.type == event_type]

        return events

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

    def context(self, entry_hash: str) -> Tuple[Directive, Any, str, str]:
        """Context for an entry.

        Arguments:
            entry_hash: Hash of entry.

        Returns:
            A tuple ``(entry, balances, source_slice, sha256sum)`` of the
            (unique) entry with the given ``entry_hash``. If the entry is a
            Balance or Transaction then ``balances`` is a 2-tuple containing
            the balances before and after the entry of the affected accounts.
        """
        entry = self.get_entry(entry_hash)
        balances = None
        if isinstance(entry, (Balance, Transaction)):
            balances = compute_entry_context(self.all_entries, entry)
        source_slice, sha256sum = get_entry_slice(entry)
        return entry, balances, source_slice, sha256sum

    def commodity_pairs(self) -> List[Tuple[str, str]]:
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

    def prices(
        self, base: str, quote: str
    ) -> List[Tuple[datetime.date, Decimal]]:
        """List all prices."""
        all_prices = get_all_prices(self.price_map, (base, quote))

        if (
            self.filters.time
            and self.filters.time.begin_date is not None
            and self.filters.time.end_date is not None
        ):
            return [
                (date, price)
                for date, price in all_prices
                if self.filters.time.begin_date
                <= date
                < self.filters.time.end_date
            ]
        return all_prices

    def last_entry(self, account_name: str) -> Optional[Directive]:
        """Get last entry of an account.

        Args:
            account_name: An account name.

        Returns:
            The last entry of the account if it is not a Close entry.
        """
        account = realization.get_or_create(
            self.all_root_account, account_name
        )

        last = realization.find_last_active_posting(account.txn_postings)

        if last is None or isinstance(last, Close):
            return None

        return get_entry(last)

    def statement_path(self, entry_hash: str, metadata_key: str) -> str:
        """Returns the path for a statement found in the specified entry."""
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

    def account_uptodate_status(self, account_name: str) -> Optional[str]:
        """Status of the last balance or transaction.

        Args:
            account_name: An account name.

        Returns:
            A status string for the last balance or transaction of the account.

            - 'green':  A balance check that passed.
            - 'red':    A balance check that failed.
            - 'yellow': Not a balance check.
        """

        real_account = realization.get_or_create(
            self.all_root_account, account_name
        )

        for txn_posting in reversed(real_account.txn_postings):
            if isinstance(txn_posting, Balance):
                if txn_posting.diff_amount:
                    return "red"
                return "green"
            if (
                isinstance(txn_posting, TxnPosting)
                and txn_posting.txn.flag != FLAG_UNREALIZED
            ):
                return "yellow"
        return None

    def account_is_closed(self, account_name: str) -> bool:
        """Check if the account is closed.

        Args:
            account_name: An account name.

        Returns:
            True if the account is closed before the end date of the current
            time filter.
        """
        if self.filters.time and self._date_last is not None:
            return self.accounts[account_name].close_date < self._date_last
        return self.accounts[account_name].close_date != datetime.date.max

    @staticmethod
    def group_entries_by_type(entries: Entries) -> List[Tuple[str, Entries]]:
        """Group the given entries by type.

        Args:
            entries: The entries to group.

        Returns:
            A list of tuples (type, entries) consisting of the directive type
            as a string and the list of corresponding entries.
        """
        groups: Dict[str, Entries] = {}
        for entry in entries:
            groups.setdefault(entry.__class__.__name__, []).append(entry)

        return sorted(list(groups.items()), key=itemgetter(0))

    def commodity_name(self, commodity: str) -> Optional[str]:
        """Return the 'name' field in metadata of a commodity
        Args:
            commodity: The commodity in string
        Returns:
            The 'name' field in metadata of a commodity if exists,
            otherwise the input string is returned
        """
        commodity_ = self.commodities.get(commodity)
        if commodity_:
            return commodity_.meta.get("name")
        return commodity
