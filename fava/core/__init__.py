"""This module provides the data required by Fava's reports."""

import collections
import copy
import datetime
import os

from beancount import loader
from beancount.core import getters, interpolate, prices, realization
from beancount.core.flags import FLAG_UNREALIZED
from beancount.core.account_types import get_account_sign
from beancount.core.compare import hash_entry
from beancount.core.data import (
    get_entry,
    iter_entry_dates,
    Open,
    Close,
    Balance,
    TxnPosting,
    Transaction,
    Event,
    Custom,
)
from beancount.parser.options import get_account_types
from beancount.utils.encryption import is_encrypted_file
from beancount.utils.misc_utils import filter_type

from fava.util import date, pairwise
from fava.core.attributes import AttributesModule
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.extensions import ExtensionModule
from fava.core.fava_options import parse_options
from fava.core.file import FileModule, get_entry_slice
from fava.core.filters import AccountFilter, AdvancedFilter, TimeFilter
from fava.core.helpers import FavaAPIException
from fava.core.ingest import IngestModule
from fava.core.misc import FavaMisc
from fava.core.number import DecimalFormatModule
from fava.core.query_shell import QueryShell
from fava.core.tree import Tree
from fava.core.watcher import Watcher


MAXDATE = datetime.date.max


class AccountData:
    """Holds information about an account."""

    __slots__ = ("meta", "close_date")

    def __init__(self):
        #: The date on which this account is closed (or datetime.date.max).
        self.close_date = MAXDATE

        #: The metadata of the Open entry of this account.
        self.meta = {}


class _AccountDict(dict):
    """Account info dictionary."""

    EMPTY = AccountData()

    def __missing__(self, key):
        return self.EMPTY

    def setdefault(self, key):
        if key not in self:
            self[key] = AccountData()
        return self[key]


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
        "_date_first",
        "_date_last",
        "entries",
        "errors",
        "fava_options",
        "_filters",
        "_is_encrypted",
        "options",
        "price_map",
        "root_account",
        "root_tree",
        "_watcher",
    ] + MODULES

    def __init__(self, path):
        #: The path to the main Beancount file.
        self.beancount_file_path = path
        self._is_encrypted = is_encrypted_file(path)
        self._filters = {}

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
        self.all_entries = None

        #: Dict of list of all (unfiltered) entries by type.
        self.all_entries_by_type = None

        #: A list of all errors reported by Beancount.
        self.errors = None

        #: A Beancount options map.
        self.options = None

        #: A Namedtuple containing the names of the five base accounts.
        self.account_types = None

        #: A dict containing information about the accounts.
        self.accounts = _AccountDict()

        #: A dict with all of Fava's option values.
        self.fava_options = None

        self.load_file()

    def load_file(self):
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
        self.price_map = prices.build_price_map(self.all_entries)
        self.all_root_account = realization.realize(
            self.all_entries, self.account_types
        )

        entries_by_type = collections.defaultdict(list)
        for entry in self.all_entries:
            entries_by_type[type(entry)].append(entry)
        self.all_entries_by_type = entries_by_type

        self.accounts = _AccountDict()
        for entry in entries_by_type[Open]:
            self.accounts.setdefault(entry.account).meta = entry.meta
        for entry in entries_by_type[Close]:
            self.accounts.setdefault(entry.account).close_date = entry.date

        self.fava_options, errors = parse_options(entries_by_type[Custom])
        self.errors.extend(errors)

        if not self._is_encrypted:
            self._watcher.update(*self.paths_to_watch())

        for mod in MODULES:
            getattr(self, mod).load_file()

        self._filters = {
            "account": AccountFilter(self.options, self.fava_options),
            "filter": AdvancedFilter(self.options, self.fava_options),
            "time": TimeFilter(self.options, self.fava_options),
        }

        self.filter(True)

    # pylint: disable=attribute-defined-outside-init
    def filter(self, force=False, **kwargs):
        """Set and apply (if necessary) filters."""
        changed = False
        for filter_name, value in kwargs.items():
            if self._filters[filter_name].set(value):
                changed = True

        if not (changed or force):
            return

        self.entries = self.all_entries

        for filter_class in self._filters.values():
            self.entries = filter_class.apply(self.entries)

        self.root_account = realization.realize(
            self.entries, self.account_types
        )
        self.root_tree = Tree(self.entries)

        self._date_first, self._date_last = getters.get_min_max_dates(
            self.entries, (Transaction)
        )
        if self._date_last:
            self._date_last = self._date_last + datetime.timedelta(1)

        if self._filters["time"]:
            self._date_first = self._filters["time"].begin_date
            self._date_last = self._filters["time"].end_date

    @property
    def end_date(self):
        """The date to use for prices."""
        if self._filters["time"]:
            return self._filters["time"].end_date
        return None

    def join_path(self, *args):
        """Path relative to the directory of the ledger."""
        include_path = os.path.dirname(self.beancount_file_path)
        return os.path.normpath(os.path.join(include_path, *args))

    def paths_to_watch(self):
        """The paths to included files and document directories.

        Returns:
            A tuple (files, directories).
        """
        files = list(self.options["include"])
        if self.fava_options["import-config"]:
            files.append(self.ingest.module_path)
        return (
            files,
            [
                self.join_path(path, account)
                for account in self.account_types
                for path in self.options["documents"]
            ],
        )

    def changed(self):
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

    def interval_ends(self, interval):
        """Generator yielding dates corresponding to interval boundaries."""
        if not self._date_first:
            return []
        return date.interval_ends(self._date_first, self._date_last, interval)

    def get_account_sign(self, account_name):
        """Get account sign.

        Arguments:
            account_name: An account name.

        Returns:
            The sign of the given account, +1 for an assets or expenses
            account, -1 otherwise.
        """
        return get_account_sign(account_name, self.account_types)

    @property
    def root_tree_closed(self):
        """A root tree for the balance sheet."""
        tree = Tree(self.entries)
        tree.cap(self.options, self.fava_options["unrealized"])
        return tree

    def interval_balances(self, interval, account_name, accumulate=False):
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

    def account_journal(self, account_name, with_journal_children=False):
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

    def events(self, event_type=None):
        """List events (possibly filtered by type)."""
        events = filter_type(self.entries, Event)

        if event_type:
            return [event for event in events if event.type == event_type]

        return list(events)

    def get_entry(self, entry_hash):
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
        except StopIteration:
            raise FavaAPIException(
                'No entry found for hash "{}"'.format(entry_hash)
            )

    def context(self, entry_hash):
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
            balances = interpolate.compute_entry_context(
                self.all_entries, entry
            )
        source_slice, sha256sum = get_entry_slice(entry)
        return entry, balances, source_slice, sha256sum

    def commodity_pairs(self):
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

    def prices(self, base, quote):
        """List all prices."""
        all_prices = prices.get_all_prices(self.price_map, (base, quote))

        if self._filters["time"]:
            return [
                (date, price)
                for date, price in all_prices
                if self._filters["time"].begin_date
                <= date
                < self._filters["time"].end_date
            ]
        return all_prices

    def last_entry(self, account_name):
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

    @property
    def postings(self):
        """All postings contained in some transaction."""
        return [
            posting
            for entry in filter_type(self.entries, Transaction)
            for posting in entry.postings
        ]

    def statement_path(self, entry_hash, metadata_key):
        """Returns the path for a statement found in the specified entry."""
        entry = self.get_entry(entry_hash)
        value = entry.meta[metadata_key]

        paths = [os.path.join(os.path.dirname(entry.meta["filename"]), value)]
        paths.extend(
            [
                self.join_path(
                    document_root, *posting.account.split(":"), value
                )
                for posting in entry.postings
                for document_root in self.options["documents"]
            ]
        )

        for path in paths:
            if os.path.isfile(path):
                return path

        raise FavaAPIException("Statement not found.")

    def account_uptodate_status(self, account_name):
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

    def account_is_closed(self, account_name):
        """Check if the account is closed.

        Args:
            account_name: An account name.

        Returns:
            True if the account is closed before the end date of the current
            time filter.
        """
        if self._filters["time"]:
            return self.accounts[account_name].close_date < self._date_last
        return self.accounts[account_name].close_date is not MAXDATE
