"""This module provides the data required by Fava's reports."""

import datetime
import os

from beancount import loader
from beancount.core import compare, flags, getters, realization
from beancount.core.account_types import get_account_sign
from beancount.core.data import (get_entry, iter_entry_dates, Open, Close,
                                 Document, Balance, TxnPosting, Transaction,
                                 Event, Query, Custom)
from beancount.ops import prices, summarize
from beancount.parser import options
from beancount.query import query
from beancount.reports import context
from beancount.utils import encryption, misc_utils

from fava.util import date
from fava.api.budgets import parse_budgets, calculate_budget
from fava.api.charts import Charts
from fava.api.watcher import Watcher
from fava.api.file import insert_metadata_in_file, next_key
from fava.api.filters import (AccountFilter, FromFilter, PayeeFilter,
                              TagFilter, TimeFilter)
from fava.api.helpers import (get_final_holdings, aggregate_holdings_by,
                              entry_at_lineno, FavaAPIException)
from fava.api.fava_options import parse_options


class FavaFileNotFoundException(Exception):
    pass


def _filter_entries_by_type(entries, include_types):
    return [entry for entry in entries if isinstance(entry, include_types)]


def _list_accounts(root_account, active_only=False):
    """List of all sub-accounts of the given root."""
    accounts = [child_account.account
                for child_account in
                realization.iter_children(root_account)
                if not active_only or child_account.txn_postings]

    return accounts if active_only else accounts[1:]


def _sidebar_links(custom_entries):
    """Parse custom entries for links.

    They have the following format:

    2016-04-01 custom "fava-sidebar-link" "2014" "/income_statement/?time=2014"
    """
    sidebar_link_entries = [
        entry for entry in custom_entries
        if entry.type == 'fava-sidebar-link']
    return [(entry.values[0].value, entry.values[1].value)
            for entry in sidebar_link_entries]


def _upcoming_events(entries, max_delta):
    """Parse entries for upcoming events.

    Args:
        entries: A list of entries.
        max_delta: Number of days that should be considered.

    Returns:
        A list of the Events in entries that are less than `max_delta` days
        away.

    """
    today = datetime.date.today()
    upcoming_events = []
    all_events = _filter_entries_by_type(entries, Event)

    for event in all_events:
        delta = event.date - today
        if delta.days >= 0 and delta.days < max_delta:
            upcoming_events.append(event)

    return upcoming_events


class BeancountReportAPI():
    """Provides methods to access and filter beancount entries.

    Attributes:
        account_types: The names for the five base accounts.
        active_payees: All payees found in the file.
        active_tags: All tags found in the file.
        active_years: All years that contain some entry.
        all_accounts: A list of all account names.
        all_accounts_active: A list of all active account names.

    """

    __slots__ = [
        '_default_format_string', '_format_string',
        'account_types', 'active_payees', 'active_tags', 'active_years',
        'all_accounts', 'all_accounts_active', 'all_entries',
        'all_root_account', 'beancount_file_path', 'budgets',
        'charts', 'custom_entries', 'date_first', 'date_last', 'entries',
        'errors', 'fava_options', 'filters', 'is_encrypted', 'options',
        'price_map', 'queries', 'root_account', 'sidebar_links', 'title',
        'upcoming_events', 'watcher']

    def __init__(self, beancount_file_path):
        self.beancount_file_path = beancount_file_path
        self.is_encrypted = encryption.is_encrypted_file(beancount_file_path)
        self.filters = {
            'account': AccountFilter(),
            'from': FromFilter(),
            'payee': PayeeFilter(),
            'tag': TagFilter(),
            'time': TimeFilter(),
        }

        self.charts = Charts(self)
        self.watcher = Watcher()
        self.load_file()

    def load_file(self):
        """Load self.beancount_file_path and compute things that are independent
        of how the entries might be filtered later"""
        # use the internal function to disable cache
        if not self.is_encrypted:
            self.all_entries, self.errors, self.options = \
                loader._load([(self.beancount_file_path, True)],
                             None, None, None)
            include_path = os.path.dirname(self.beancount_file_path)
            self.watcher.update(self.options['include'], [
                os.path.join(include_path, path)
                for path in self.options['documents']])
        else:
            self.all_entries, self.errors, self.options = \
                loader.load_file(self.beancount_file_path)
        self.price_map = prices.build_price_map(self.all_entries)
        self.account_types = options.get_account_types(self.options)

        self.title = self.options['title']
        if self.options['render_commas']:
            self._format_string = '{:,f}'
            self._default_format_string = '{:,.2f}'
        else:
            self._format_string = '{:f}'
            self._default_format_string = '{:.2f}'

        self.active_years = list(getters.get_active_years(self.all_entries))
        self.active_tags = list(getters.get_all_tags(self.all_entries))
        self.active_payees = list(getters.get_all_payees(self.all_entries))

        self.queries = _filter_entries_by_type(self.all_entries, Query)
        self.custom_entries = _filter_entries_by_type(self.all_entries, Custom)

        self.all_root_account = realization.realize(self.all_entries,
                                                    self.account_types)
        self.all_accounts = _list_accounts(self.all_root_account)
        self.all_accounts_active = _list_accounts(
            self.all_root_account, active_only=True)

        self.fava_options, errors = parse_options(self.custom_entries)
        self.errors.extend(errors)

        self.sidebar_links = _sidebar_links(self.custom_entries)

        self.upcoming_events = _upcoming_events(
            self.all_entries, self.fava_options['upcoming-events'])

        self.budgets, errors = parse_budgets(self.custom_entries)
        self.errors.extend(errors)

        self._apply_filters()

    def _apply_filters(self):
        self.entries = self.all_entries

        for filter_class in self.filters.values():
            self.entries = filter_class.apply(self.entries, self.options)

        self.root_account = realization.realize(self.entries,
                                                self.account_types)

        self.date_first, self.date_last = \
            getters.get_min_max_dates(self.entries, (Transaction))
        if self.date_last:
            self.date_last = self.date_last + datetime.timedelta(1)

        if self.filters['time']:
            self.date_first = self.filters['time'].begin_date
            self.date_last = self.filters['time'].end_date

    def filter(self, **kwargs):
        """Set and apply (if necessary) filters."""
        changed = False
        for filter_name, filter_class in self.filters.items():
            if filter_class.set(kwargs[filter_name]):
                changed = True

        if changed:
            self._apply_filters()

    def hash_entry(self, entry):
        return compare.hash_entry(entry)

    def changed(self):
        """Check if the file needs to be reloaded. """
        # We can't reload an encrypted file, so act like it never changes.
        if self.is_encrypted:
            return False
        changed = self.watcher.check()
        if changed:
            self.load_file()
        return changed

    def quantize(self, value, currency):
        """Quantize the value to the right number of decimal digits.

        Uses the DisplayContext generated by beancount."""
        if not currency:
            return self._default_format_string.format(value)
        return self._format_string.format(
            self.options['dcontext'].quantize(value, currency))

    def _interval_tuples(self, interval):
        """Calculates tuples of (begin_date, end_date) of length interval for the
        period in which entries contains transactions.  """
        return date.interval_tuples(self.date_first, self.date_last, interval)

    def get_account_sign(self, account_name):
        return get_account_sign(account_name, self.account_types)

    def balances(self, account_name):
        return realization.get_or_create(self.root_account, account_name)

    def closing_balances(self, account_name):
        closing_entries = summarize.cap_opt(self.entries, self.options)
        return realization.get_or_create(realization.realize(closing_entries),
                                         account_name)

    def interval_balances(self, interval, account_name, accumulate=False):
        """accumulate is False for /changes and True for /balances"""
        min_accounts = [account
                        for account in self.all_accounts
                        if account.startswith(account_name)]

        interval_tuples = list(reversed(self._interval_tuples(interval)))

        interval_balances = [
            realization.realize(list(iter_entry_dates(
                self.entries,
                self.date_first if accumulate else begin_date,
                end_date)), min_accounts)
            for begin_date, end_date in interval_tuples]

        return interval_balances, interval_tuples

    def calculate_budget(self, account_name, begin_date, end_date):
        return calculate_budget(self.budgets, account_name, begin_date,
                                end_date)

    def account_journal(self, account_name, with_journal_children=False):
        real_account = realization.get_or_create(self.root_account,
                                                 account_name)

        if with_journal_children:
            postings = realization.get_postings(real_account)
        else:
            postings = real_account.txn_postings

        return realization.iterate_with_balance(postings)

    def get_query(self, name):
        return next((query for query in self.queries if name == query.name),
                    None)

    def events(self, event_type=None):
        events = _filter_entries_by_type(self.entries, Event)

        if event_type:
            return [event for event in events if event.type == event_type]

        return events

    def holdings(self, aggregation_key=None):
        holdings_list = get_final_holdings(
            self.entries,
            (self.account_types.assets, self.account_types.liabilities),
            self.price_map,
            self.date_last
        )

        if aggregation_key:
            holdings_list = aggregate_holdings_by(holdings_list,
                                                  aggregation_key)
        return holdings_list

    def context(self, ehash):
        try:
            entry = next(entry for entry in self.all_entries
                         if ehash == compare.hash_entry(entry))
        except StopIteration:
            return

        context_str = context.render_entry_context(self.all_entries,
                                                   self.options, entry)
        return {
            'context': context_str.split("\n", 2)[2],
            'entry': entry,
        }

    def source_files(self):
        """List source files.

        Returns:
            A list of all sources files, with the main file listed first.

        """
        return [self.beancount_file_path] + \
            sorted(filter(
                lambda x: x != self.beancount_file_path,
                [os.path.join(
                    os.path.dirname(self.beancount_file_path), filename)
                 for filename in self.options['include']]))

    def source(self, file_path):
        """Get source files.

        Args:
            file_path: The path of the file.

        Returns:
            A string with the file contents.

        Raises:
            FavaAPIException: If the file at `file_path` is not one of the
                source files.

        """
        if file_path not in self.source_files():
            raise FavaAPIException('Trying to read a non-source file')

        with open(file_path, encoding='utf8') as file:
            source = file.read()
        return source

    def set_source(self, file_path, source):
        """Write to source file.

        Args:
            file_path: The path of the file.
            source: A string with the file contents.

        Raises:
            FavaAPIException: If the file at `file_path` is not one of the
                source files.

        """
        if file_path not in self.source_files():
            raise FavaAPIException('Trying to write a non-source file')

        with open(file_path, 'w+', encoding='utf8') as file:
            file.write(source)
        self.load_file()

    def commodity_pairs(self):
        """List pairs of commodities.

        Returns:
            A list of pairs of commodities. Pairs of operating currencies will
            be given in both directions not just in the one found in file.

        """
        fw_pairs = self.price_map.forward_pairs
        bw_pairs = []
        for currency_a, currency_b in fw_pairs:
            if (currency_a in self.options['operating_currency'] and
                    currency_b in self.options['operating_currency']):
                bw_pairs.append((currency_b, currency_a))
        return sorted(fw_pairs + bw_pairs)

    def prices(self, base, quote):
        all_prices = prices.get_all_prices(self.price_map,
                                           "{}/{}".format(base, quote))

        if self.filters['time']:
            return [(date, price) for date, price in all_prices
                    if (date >= self.filters['time'].begin_date and
                        date < self.filters['time'].end_date)]
        else:
            return all_prices

    def last_entry(self, account_name):
        """Get last entry of an account.

        Args:
            account_name: An account name.

        Returns:
            The last entry of the account if it is not a Close entry.
        """
        account = realization.get_or_create(self.all_root_account,
                                            account_name)

        last = realization.find_last_active_posting(account.txn_postings)

        if last is None or isinstance(last, Close):
            return

        return get_entry(last)

    def postings_by_account(self):
        all_postings = [posting
                        for entry in self.entries
                        if isinstance(entry, Transaction)
                        for posting in entry.postings]

        grouped_postings = misc_utils.groupby(
            lambda posting: posting.account, all_postings)
        return {account: len(postings) for account, postings
                in grouped_postings.items()}

    def abs_path(self, file_path):
        """Make a path absolute.

        Args:
            file_path: A file path.

        Returns:
            The absolute path of `file_path`, assuming it is relative to
            the directory of the beancount file.

        """
        if not os.path.isabs(file_path):
            return os.path.join(os.path.dirname(
                os.path.realpath(self.beancount_file_path)), file_path)
        return file_path

    def statement_path(self, filename, lineno, metadata_key):
        """Returns the path for a statement found in the specified entry."""
        entry = entry_at_lineno(self.entries, filename, lineno, Transaction)
        value = entry.meta[metadata_key]

        paths = [value]
        paths.extend([os.path.join(posting.account.replace(':', '/'), value)
                      for posting in entry.postings])
        paths.extend([os.path.join(document_root,
                                   posting.account.replace(':', '/'), value)
                      for posting in entry.postings
                      for document_root in self.options['documents']])

        for path in [self.abs_path(p) for p in paths]:
            if os.path.isfile(path):
                return path

        raise FavaFileNotFoundException()

    def document_path(self, file_path):
        """Get absolute path of a document.

        Returns:
            The absolute path of `file_path` if it points to a document.

        Raises:
            FavaFileNotFoundException: If `path` is not the path to one of the
                documents.

        """
        for entry in misc_utils.filter_type(self.entries, Document):
            if entry.filename == file_path:
                return self.abs_path(file_path)

        raise FavaFileNotFoundException()

    def query(self, query_string, numberify=False):
        return query.run_query(self.all_entries, self.options,
                               query_string, numberify=numberify)

    def _last_balance_or_transaction(self, account_name):
        real_account = realization.get_or_create(self.all_root_account,
                                                 account_name)

        for txn_posting in reversed(real_account.txn_postings):
            if not isinstance(txn_posting, (TxnPosting, Balance)):
                continue

            if isinstance(txn_posting, TxnPosting) and \
               txn_posting.txn.flag == flags.FLAG_UNREALIZED:
                continue
            return txn_posting

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
        last_posting = self._last_balance_or_transaction(account_name)

        if last_posting:
            if isinstance(last_posting, Balance):
                if last_posting.diff_amount:
                    return 'red'
                else:
                    return 'green'
            else:
                return 'yellow'

    def account_metadata(self, account_name):
        """Metadata of the account.

        Args:
            account_name: An account name.

        Returns:
            Metadata of the Open entry of the account.
        """
        real_account = realization.get_or_create(self.root_account,
                                                 account_name)
        for posting in real_account.txn_postings:
            if isinstance(posting, Open):
                return posting.meta
        return {}

    def insert_metadata(self, filename, lineno, basekey, value):
        """Insert metadata into a file at lineno.

        Also, prevent duplicate keys.
        """
        entry = entry_at_lineno(self.entries, filename, lineno, Transaction)
        key = next_key(basekey, entry.meta)
        insert_metadata_in_file(filename, lineno-1, key, value)
