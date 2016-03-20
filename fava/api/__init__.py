"""
The rationale behind this API is the following:

One day there will be a new module in beancount.report that returns all (for
fava required) views as Python-dicts and -arrays, compatible with
JSON (so no datetime, etc.). Right now beancount.report does return data to
be displayed in a console, and HTML, and this (JSON) could be a third way of
"rendering" the data. These methods should be highly optimized for performance
and numerical correctness. If that one day really makes it's way into the
beancount-repo, then api.py is redundant and will be removed.

For the JSON-part: I want to keep all the returns in the API JSON-serializeable
(although they are called directly right now), because then, with very little
overhead, fava could run on an external server and call into a local
bean-report.

Right now this module it is just a hacky placeholder for what could be in the
future, and therefore I only tried to get the numbers required, and did not
optimize for performance at all.
"""

import datetime
import operator
import os

from beancount import loader
from beancount.core import compare, getters, realization, inventory
from beancount.core.realization import RealAccount
from beancount.core.interpolate import compute_entries_balance
from beancount.core.account import has_component
from beancount.core.account_types import get_account_sign
from beancount.core.data import (get_entry, iter_entry_dates, Open, Close,
                                 Note, Document, Balance, Transaction, Event,
                                 Query)
from beancount.ops import prices, holdings, summarize
from beancount.parser import options
from beancount.query import query
from beancount.reports import context
from beancount.utils import misc_utils

from fava.util.date import parse_date, get_next_interval
from fava.api.helpers import holdings_at_dates
from fava.api.serialization import (serialize_inventory, serialize_entry,
                                    serialize_entry_with,
                                    serialize_real_account)


class FilterException(Exception):
    pass


class EntryFilter(object):
    def __init__(self):
        self.value = None

    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        return True

    def _include_entry(self, entry):
        raise NotImplementedError

    def _filter(self, entries, options):
        return [entry for entry in entries if self._include_entry(entry)]

    def apply(self, entries, options):
        if self.value:
            return self._filter(entries, options)
        else:
            return entries


class DateFilter(EntryFilter):
    def set(self, value):
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True
        try:
            self.begin_date, self.end_date = parse_date(self.value)
        except TypeError:
            raise FilterException('Failed to parse date: {}'
                                  .format(self.value))
        return True

    def _filter(self, entries, options):
        entries, _ = summarize.clamp_opt(entries, self.begin_date,
                                         self.end_date, options)
        return entries


class TagFilter(EntryFilter):
    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            entry.tags and (entry.tags & set(self.value))


class AccountFilter(EntryFilter):
    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            any(has_component(posting.account, self.value)
                for posting in entry.postings)


class PayeeFilter(EntryFilter):
    def _include_entry(self, entry):
        return isinstance(entry, Transaction) and \
            ((entry.payee and (entry.payee in self.value)) or
             (not entry.payee and ('' in self.value)))


class BeancountReportAPI(object):
    def __init__(self, beancount_file_path=None):
        self.beancount_file_path = beancount_file_path
        self.filters = {
            'time': DateFilter(),
            'tag': TagFilter(),
            'account': AccountFilter(),
            'payee': PayeeFilter(),
        }
        if self.beancount_file_path:
            self.load_file()

    def load_file(self, beancount_file_path=None):
        """Load self.beancount_file_path and compute things that are independent
        of how the entries might be filtered later"""
        if beancount_file_path:
            self.beancount_file_path = beancount_file_path

        self.all_entries, self.errors, self.options = \
            loader.load_file(self.beancount_file_path)
        self.price_map = prices.build_price_map(self.all_entries)
        self.account_types = options.get_account_types(self.options)

        self.title = self.options['title']
        if self.options['render_commas']:
            self.format_string = '{:,f}'
            self.default_format_string = '{:,.2f}'
        else:
            self.format_string = '{:f}'
            self.default_format_string = '{:.2f}'
        self.dcontext = self.options['dcontext']

        self.active_years = list(getters.get_active_years(self.all_entries))
        self.active_tags = list(getters.get_all_tags(self.all_entries))
        self.active_payees = list(getters.get_all_payees(self.all_entries))

        self.all_root_account = realization.realize(self.all_entries,
                                                    self.account_types)
        self.all_accounts = self._all_accounts()
        self.all_accounts_leaf_only = self._all_accounts(leaf_only=True)

        self._apply_filters()

    def _apply_filters(self):
        self.entries = self.all_entries

        for filter in self.filters.values():
            self.entries = filter.apply(self.entries, self.options)

        self.root_account = realization.realize(self.entries,
                                                self.account_types)

    def filter(self, **kwargs):
        changed = False
        for filter_name, filter in self.filters.items():
            if filter.set(kwargs[filter_name]):
                changed = True

        if changed:
            self._apply_filters()

    def _all_accounts(self, leaf_only=False):
        """Detailed list of all accounts."""
        accounts = [child_account.account
                    for child_account in
                    realization.iter_children(self.all_root_account,
                                              leaf_only=leaf_only)]

        return accounts[1:]

    def quantize(self, value, currency):
        if not currency:
            return self.default_format_string.format(value)
        return self.format_string.format(self.dcontext.quantize(value,
                                                                currency))

    def _journal(self, entries, include_types=None,
                 with_change_and_balance=False):
        if include_types:
            entries = [entry for entry in entries
                       if isinstance(entry, include_types)]

        if not with_change_and_balance:
            return [serialize_entry(entry) for entry in entries]
        else:
            return [serialize_entry_with(entry, change, balance)
                    for entry, _, change, balance in
                    realization.iterate_with_balance(entries)]

    def _interval_tuples(self, interval, entries):
        """
        Calculates tuples of (begin_date, end_date) of length interval for the
        period in which entries contains Transactions.

        Args:
            interval: Either 'month' or 'year'

        Returns:
            [
                (begin_date, end_date),
                ...
            ]
        """
        date_first, date_last = getters.get_min_max_dates(entries,
                                                          (Transaction))

        if not date_first:
            return []

        interval_tuples = []
        while date_first <= date_last:
            next_date = get_next_interval(date_first, interval)
            interval_tuples.append((date_first, next_date))
            date_first = next_date

        return interval_tuples

    def _total_balance(self, names, begin_date, end_date):
        totals = [realization.compute_balance(
            self._real_account(account_name, self.entries, begin_date,
                               end_date))
                  for account_name in names]
        return serialize_inventory(sum(totals, inventory.Inventory()),
                                   at_cost=True)

    def interval_totals(self, interval, account_name, accumulate=False):
        """Renders totals for account (or accounts) in the intervals."""
        if isinstance(account_name, str):
            names = [account_name]
        else:
            names = account_name

        interval_tuples = self._interval_tuples(interval, self.entries)
        date_first, _ = getters.get_min_max_dates(self.entries, (Transaction))
        return [{
            'begin_date': begin_date,
            'end_date': end_date,
            'totals': self._total_balance(
                names, begin_date if not accumulate else date_first, end_date),
        } for begin_date, end_date in interval_tuples]

    def _real_account(self, account_name, entries, begin_date=None,
                      end_date=None, min_accounts=None):
        """
        Returns the realization.RealAccount instances for account_name, and
        their entries clamped by the optional begin_date and end_date.

        Warning: For efficiency, the returned result does not include any added
        postings to account for balances at 'begin_date'.

        :return: realization.RealAccount instances
        """
        if begin_date:
            entries = list(iter_entry_dates(entries, begin_date, end_date))
        if not min_accounts:
            min_accounts = [account_name]

        return realization.get(realization.realize(entries, min_accounts),
                               account_name)

    def balances(self, account_name, begin_date=None, end_date=None):
        real_account = self._real_account(account_name, self.entries,
                                          begin_date, end_date)
        return [serialize_real_account(real_account)]

    def closing_balances(self, account_name):
        closing_entries = summarize.cap_opt(self.entries, self.options)
        return [serialize_real_account(self._real_account(account_name,
                                                          closing_entries))]

    def _flatten(self, serialized_real_account):
        list_ = [serialized_real_account]
        for ra in serialized_real_account['children']:
            list_.extend(self._flatten(ra))
        return list_

    def interval_balances(self, interval, account_name, accumulate=False):
        account_names = [account
                         for account in self.all_accounts
                         if account.startswith(account_name)]

        interval_tuples = self._interval_tuples(interval, self.entries)
        interval_balances = [self._flatten(serialize_real_account(
            self._real_account(
                account_name, self.entries,
                interval_tuples[0][0] if accumulate else begin_date,
                end_date, min_accounts=account_names)))
            for begin_date, end_date in interval_tuples]
        return list(zip(*interval_balances)), interval_tuples

    def trial_balance(self):
        return serialize_real_account(self.root_account)['children']

    def journal(self, account_name=None, with_change_and_balance=False,
                with_journal_children=True):
        if account_name:
            real_account = realization.get_or_create(self.root_account,
                                                     account_name)

            if with_journal_children:
                postings = realization.get_postings(real_account)
            else:
                postings = real_account.txn_postings

            return self._journal(postings, with_change_and_balance=True)
        else:
            return self._journal(
                self.entries, with_change_and_balance=with_change_and_balance)

    def documents(self):
        return self._journal(self.entries, Document)

    def notes(self):
        return self._journal(self.entries, Note)

    def queries(self, query_hash=None):
        if not query_hash:
            return self._journal(self.all_entries, Query)
        matching_entries = [entry for entry in self.all_entries
                            if query_hash == compare.hash_entry(entry)]

        if not matching_entries:
            return

        assert len(matching_entries) == 1
        return serialize_entry(matching_entries[0])

    def events(self, event_type=None, only_include_newest=False):
        events = self._journal(self.entries, Event)

        if event_type:
            events = [event for event in events if event['type'] == event_type]

        if only_include_newest:
            seen_types = list()
            for event in events:
                if not event['type'] in seen_types:
                    seen_types.append(event['type'])
            events = list({event['type']: event for event in events}.values())

        return events

    def holdings(self, aggregation_key=None):
        holdings_list = holdings.get_final_holdings(
            self.entries,
            (self.account_types.assets, self.account_types.liabilities),
            self.price_map)

        if aggregation_key:
            holdings_list = holdings.aggregate_holdings_by(
                holdings_list, operator.attrgetter(aggregation_key))
        return holdings_list

    def _net_worth_in_intervals(self, interval):
        interval_tuples = self._interval_tuples(interval, self.entries)
        interval_totals = []
        end_dates = [p[1] for p in interval_tuples]

        for (begin_date, end_date), holdings_list in \
                zip(interval_tuples,
                    holdings_at_dates(self.entries, end_dates,
                                      self.price_map, self.options)):
            totals = {}
            for currency in self.options['operating_currency']:
                currency_holdings_list = \
                    holdings.convert_to_currency(self.price_map, currency,
                                                 holdings_list)
                if not currency_holdings_list:
                    continue

                holdings_ = holdings.aggregate_holdings_by(
                    currency_holdings_list,
                    operator.attrgetter('cost_currency'))

                holdings_ = [holding
                             for holding in holdings_
                             if holding.currency and holding.cost_currency]

                # If after conversion there are no valid holdings, skip the
                # currency altogether.
                if holdings_:
                    totals[currency] = holdings_[0].market_value

            interval_totals.append({
                'date': end_date - datetime.timedelta(1),
                'totals': totals
            })
        return interval_totals

    def net_worth(self, interval='month'):
        interval_totals = self._net_worth_in_intervals(interval)
        if interval_totals:
            current = interval_totals[-1]['totals']
        else:
            current = {}
        return {
            'net_worth': current,
            'interval_totals': interval_totals
        }

    def context(self, ehash):
        matching_entries = [entry for entry in self.all_entries
                            if ehash == compare.hash_entry(entry)]

        if not matching_entries:
            return

        # the hash should uniquely identify the entry
        assert len(matching_entries) == 1
        entry = matching_entries[0]
        context_str = context.render_entry_context(self.all_entries,
                                                   self.options, entry)
        ctx = context_str.split("\n", 2)
        filenamelineno = ctx[1]
        filename = filenamelineno.split(":")[1].strip()
        lineno = int(filenamelineno.split(":")[2].strip())

        return {
            'hash': ehash,
            'context': ctx[2],
            'filename': filename,
            'line': lineno,
            'journal': self._journal(matching_entries)
        }

    def treemap_data(self, account_name, begin_date=None, end_date=None):
        return {
            'label': account_name,
            'balances': self.balances(account_name, begin_date, end_date),
            'modifier': get_account_sign(account_name, self.account_types),
        }

    def linechart_data(self, account_name):
        journal = self.journal(account_name, with_change_and_balance=True)

        return [{
            'date': journal_entry['date'],
            'balance': journal_entry['balance'],
            'change': journal_entry['change'],
        } for journal_entry in journal if 'balance' in journal_entry.keys()]

    def source_files(self):
        # Make sure the included source files are sorted, behind the main
        # source file
        return [self.beancount_file_path] + \
            sorted(filter(
                lambda x: x != self.beancount_file_path,
                [os.path.join(
                    os.path.dirname(self.beancount_file_path), filename)
                 for filename in self.options['include']]))

    def source(self, file_path=None):
        if file_path:
            if file_path in self.source_files():
                with open(file_path, encoding='utf8') as f:
                    source_ = f.read()
                return source_
            else:
                return None  # TODO raise

        return self._source

    def set_source(self, file_path, source):
        if file_path in self.source_files():
            with open(file_path, 'w+', encoding='utf8') as f:
                f.write(source)
            return True
        else:
            return False  # TODO raise

    def commodity_pairs(self):
        fw_pairs = self.price_map.forward_pairs
        bw_pairs = []
        for a, b in fw_pairs:
            if (a in self.options['operating_currency'] and
                    b in self.options['operating_currency']):
                bw_pairs.append((b, a))
        return sorted(fw_pairs + bw_pairs)

    def prices(self, base, quote):
        return prices.get_all_prices(self.price_map,
                                     "{}/{}".format(base, quote))

    def _activity_by_account(self, account_name=None):
        nb_activity_by_account = []
        for real_account in realization.iter_children(self.root_account):
            if not isinstance(real_account, RealAccount):
                continue
            if account_name and real_account.account != account_name:
                continue

            last_posting = realization.find_last_active_posting(
                real_account.txn_postings)

            if last_posting is None or isinstance(last_posting, Close):
                continue

            entry = get_entry(last_posting)

            nb_activity_by_account.append({
                'account': real_account.account,
                'last_posting_date': entry.date,
                'last_posting_filename': entry.meta['filename'],
                'last_posting_lineno': entry.meta['lineno']
            })

        return nb_activity_by_account

    def inventory(self, account_name):
        return compute_entries_balance(self.entries, prefix=account_name)

    def statistics(self, account_name=None):
        if account_name:
            activity_by_account = self._activity_by_account(account_name)
            if len(activity_by_account) == 1:
                return activity_by_account[0]
            else:
                return None

        # nb_entries_by_type
        entries_by_type = misc_utils.groupby(
            lambda entry: type(entry).__name__, self.entries)
        nb_entries_by_type = {name: len(entries)
                              for name, entries in entries_by_type.items()}

        all_postings = [posting
                        for entry in self.entries
                        if isinstance(entry, Transaction)
                        for posting in entry.postings]

        # nb_postings_by_account
        postings_by_account = misc_utils.groupby(
            lambda posting: posting.account, all_postings)
        nb_postings_by_account = {account: len(postings)
                                  for account, postings
                                  in postings_by_account.items()}

        return {
            'entries_by_type':           nb_entries_by_type,
            'entries_by_type_total':     sum(nb_entries_by_type.values()),
            'postings_by_account':       nb_postings_by_account,
            'postings_by_account_total': sum(nb_postings_by_account.values()),
            'activity_by_account':       self._activity_by_account()
        }

    def is_valid_document(self, file_path):
        """Check if the given file_path is present in one of the
           Document entries or in a "statement"-metadata in a Transaction
           entry.

           :param file_path: A path to a file.
           :return: True when the file_path is refered to in a Document entry,
                    False otherwise.
        """
        is_present = False
        for entry in misc_utils.filter_type(self.entries, Document):
            if entry.filename == file_path:
                is_present = True

        if not is_present:
            for entry in misc_utils.filter_type(self.entries, Transaction):
                if 'statement' in entry.meta and \
                        entry.meta['statement'] == file_path:
                    is_present = True

        return is_present

    def query(self, bql_query_string, numberify=False):
        return query.run_query(self.all_entries, self.options,
                               bql_query_string, numberify=numberify)

    def _last_posting_for_account(self, account_name):
        """
        Returns the last posting for an account (ignores Close)
        """
        real_account = realization.get_or_create(self.all_root_account,
                                                 account_name)

        last_posting = realization.find_last_active_posting(
            real_account.txn_postings)

        if not isinstance(last_posting, Close):
            return last_posting

        postings = realization.get_postings(real_account)
        if len(postings) >= 2:
            return postings[-2]

        return None

    def is_account_uptodate(self, account_name, look_back_days=60):
        """
        green:  if the last entry is a balance check that passed
        red:    if the last entry is a balance check that failed
        yellow: if the last entry is not a balance check
        """

        last_posting = self._last_posting_for_account(account_name)

        if last_posting:
            if isinstance(last_posting, Balance):
                if last_posting.diff_amount:
                    return 'red'
                else:
                    return 'green'
            else:
                return 'yellow'
        else:
            return None

    def last_account_activity_in_days(self, account_name):
        real_account = realization.get_or_create(self.all_root_account,
                                                 account_name)

        last_posting = realization.find_last_active_posting(
            real_account.txn_postings)

        if last_posting is None or isinstance(last_posting, Close):
            return 0

        entry = get_entry(last_posting)

        return (datetime.date.today() - entry.date).days

    def account_open_metadata(self, account_name):
        real_account = realization.get_or_create(self.root_account,
                                                 account_name)
        postings = realization.get_postings(real_account)
        for posting in postings:
            if isinstance(posting, Open):
                return posting.meta
        return {}
