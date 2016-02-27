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

import operator
import os
from datetime import date

from beancount import loader
from beancount.core import compare, getters, realization, inventory
from beancount.core.realization import RealAccount
from beancount.core.interpolate import compute_entries_balance
from beancount.core.account import has_component
from beancount.core.account_types import get_account_sign
from beancount.core.data import (get_entry, iter_entry_dates, posting_sortkey,
                                 Open, Close, Note, Document, Balance,
                                 Transaction, Event, Query)
from beancount.ops import prices, holdings, summarize
from beancount.parser import options
from beancount.query import query
from beancount.reports import context
from beancount.utils import misc_utils

from fava.util.dateparser import parse_date
from fava.api.helpers import holdings_at_dates
from fava.api.serialization import serialize_inventory, serialize_entry


def get_next_interval(date_, interval):
    if interval == 'year':
        return date(date_.year + 1, 1, 1)
    elif interval == 'month':
        month = (date_.month % 12) + 1
        year = date_.year + (date_.month + 1 > 12)
        return date(year, month, 1)
    else:
        raise NotImplementedError


class FilterException(Exception):
    pass


class BeancountReportAPI(object):
    def __init__(self, beancount_file_path=None):
        self.beancount_file_path = beancount_file_path
        self.filters = {
            'time': None,
            'tag': set(),
            'account': None,
            'payee': set(),
        }
        if self.beancount_file_path:
            self.load_file()

    def load_file(self, beancount_file_path=None):
        """Load self.beancount_file_path and compute things that are independent
        of how the entries might be filtered later"""
        if beancount_file_path:
            self.beancount_file_path = beancount_file_path

        self.all_entries, self._errors, self.options = loader.load_file(self.beancount_file_path)
        self.price_map = prices.build_price_map(self.all_entries)
        self.account_types = options.get_account_types(self.options)

        self.title = self.options['title']

        self.errors = []
        for error in self._errors:
            self.errors.append({
                'file': error.source['filename'],
                'line': error.source['lineno'],
                'error': error.message
            })

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

        if self.filters['time']:
            try:
                begin_date, end_date = parse_date(self.filters['time'])
                self.entries, _ = summarize.clamp_opt(self.entries, begin_date, end_date, self.options)
            except TypeError:
                raise FilterException('Failed to parse date string: {}'.format(self.filters['time']))

        if self.filters['tag']:
            self.entries = [entry
                            for entry in self.entries
                            if isinstance(entry, Transaction) and entry.tags and (entry.tags & set(self.filters['tag']))]

        if self.filters['payee']:
            self.entries = [entry
                            for entry in self.entries
                            if (isinstance(entry, Transaction) and entry.payee and (entry.payee in self.filters['payee']))
                            or (isinstance(entry, Transaction) and not entry.payee and ('' in self.filters['payee']))]

        if self.filters['account']:
            self.entries = [entry
                            for entry in self.entries
                            if isinstance(entry, Transaction) and
                                any(has_component(posting.account, self.filters['account'])
                                    for posting in entry.postings)]

        self.root_account = realization.realize(self.entries, self.account_types)

    def filter(self, **kwargs):
        changed = False
        for filter, current_value in self.filters.items():
            if filter in kwargs and kwargs[filter] != current_value:
                self.filters[filter] = kwargs[filter]
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

    def _table_tree(self, real_account):
        """
        Renders real_account and it's children as a flat list to be used
        in rendering tables.
        """
        return [{
            'account': ra.account,
            'balances_children': serialize_inventory(realization.compute_balance(ra), at_cost=True),
            'balances': serialize_inventory(ra.balance, at_cost=True),
            'is_leaf': len(ra) == 0 or bool(ra.txn_postings),
            'postings_count': len(ra.txn_postings)
        } for ra in realization.iter_children(real_account)]

    def _journal(self, postings, include_types=None, with_change_and_balance=False):
        journal = []

        for posting, leg_postings, change, entry_balance in realization.iterate_with_balance(postings):

            if include_types and not isinstance(posting, include_types):
                continue

            entry = serialize_entry(posting)

            if with_change_and_balance:
                if isinstance(posting, Balance):
                    entry['change'] = {}
                    if posting.diff_amount:
                        entry['change'] = {posting.diff_amount.currency: posting.diff_amount.number}
                    entry['balance'] = serialize_inventory(entry_balance)

                if isinstance(posting, Transaction):
                    entry['change'] = serialize_inventory(change)
                    entry['balance'] = serialize_inventory(entry_balance)

            journal.append(entry)

        return journal

    def _interval_tuples(self, interval, entries):
        """
        Calculates tuples of (begin_date, end_date) of length interval for the period in
        which entries contains Transactions.

        Args:
            interval: Either 'month' or 'year'

        Returns:
            [
                (begin_date, end_date),
                ...
            ]
        """
        date_first, date_last = getters.get_min_max_dates(entries, (Transaction))

        if not date_first:
            return []

        interval_tuples = []
        while date_first <= date_last:
            next_date = get_next_interval(date_first, interval)
            interval_tuples.append((date_first, next_date))
            date_first = next_date

        return interval_tuples

    def _balances_totals(self, names, begin_date, end_date):
        totals = [realization.compute_balance(self._real_account(account_name, self.entries, begin_date, end_date)) for account_name in names]
        return serialize_inventory(sum(totals, inventory.Inventory()), at_cost=True)

    def interval_totals(self, interval, account_name, accumulate=False):
        """Renders totals for account (or accounts) in the intervals."""
        names = [account_name] if isinstance(account_name, str) else account_name

        interval_tuples = self._interval_tuples(interval, self.entries)
        date_first, _ = getters.get_min_max_dates(self.entries, (Transaction))
        return [{
            'begin_date': begin_date,
            'end_date': end_date,
            'totals': self._balances_totals(names, begin_date if not accumulate else date_first, end_date),
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

    def balances(self, account_name, begin_date=None, end_date=None, min_accounts=None):
        """
        Renders account_name and it's children as a flat list to be used
        in rendering tables.

        Returns:
          [
              {
                  'account': 'Expenses:Vacation',
                  'balances_children': {
                      'USD': 123.45, ...
                  },
                  'balances': {
                      'USD': 123.45, ...
                  },
                  'is_leaf': True,
                  'postings_count': 3
              }, ...
          ]
        """
        real_account = self._real_account(account_name, self.entries, begin_date, end_date, min_accounts)

        return self._table_tree(real_account)

    def closing_balances(self, account_name):
        closing_entries = summarize.cap_opt(self.entries, self.options)
        return self._table_tree(self._real_account(account_name, closing_entries))

    def interval_balances(self, interval, account_name, accumulate=False):
        account_names = [account
                         for account in self.all_accounts
                         if account.startswith(account_name)]

        interval_tuples = self._interval_tuples(interval, self.entries)
        if accumulate:
            interval_balances = [self.balances(account_name, interval_tuples[0][0], end_date,
                                               min_accounts=account_names)
                                 for begin_date, end_date in interval_tuples]
        else:
            interval_balances = [self.balances(account_name, begin_date, end_date,
                                               min_accounts=account_names)
                                 for begin_date, end_date in interval_tuples]
        return list(zip(*interval_balances)), interval_tuples

    def trial_balance(self):
        return self._table_tree(self.root_account)[1:]

    def journal(self, account_name=None, with_change_and_balance=False, with_journal_children=True):
        if account_name:
            real_account = realization.get_or_create(self.root_account, account_name)

            if with_journal_children:
                postings = realization.get_postings(real_account)
            else:
                postings = []
                postings.extend(real_account.txn_postings)
                postings.sort(key=posting_sortkey)

            return self._journal(postings, with_change_and_balance=with_change_and_balance)
        else:
            return self._journal(self.entries, with_change_and_balance=with_change_and_balance)

    def documents(self):
        return self._journal(self.entries, Document)

    def notes(self):
        return self._journal(self.entries, Note)

    def queries(self, query_hash=None):
        res = self._journal(self.all_entries, Query)
        no_query = {
            'name': 'None',
            'query_string': ''
        }
        if query_hash:
            return next( (x for x in res if x['hash'] == query_hash), no_query)
        else:
            return res

    def events(self, event_type=None, only_include_newest=False):
        events = self._journal(self.entries, Event)

        if event_type:
            events = [event for event in events if event['type'] == event_type]

        if only_include_newest:
            seen_types = list()
            for event in events:
                if not event['type'] in seen_types:
                    seen_types.append(event['type'])
            events = list({ event['type']: event for event in events }.values())

        return events

    def holdings(self, aggregation_key=None):
        holdings_list = holdings.get_final_holdings(self.entries,
                                                    (self.account_types.assets,
                                                     self.account_types.liabilities),
                                                    self.price_map)
        if aggregation_key:
            holdings_list = holdings.aggregate_holdings_by(holdings_list,
                                                           operator.attrgetter(aggregation_key))
        return holdings_list

    def _net_worth_in_periods(self):
        month_tuples = self._interval_tuples('month', self.entries)
        monthly_totals = []
        end_dates = [p[1] for p in month_tuples]

        for (begin_date, end_date), holdings_list in \
                zip(month_tuples, holdings_at_dates(self.entries, end_dates,
                                                    self.price_map, self.options)):
            totals = {}
            for currency in self.options['operating_currency']:
                currency_holdings_list = \
                    holdings.convert_to_currency(self.price_map, currency,
                                                 holdings_list)
                if not currency_holdings_list:
                    continue

                holdings_list = holdings.aggregate_holdings_by(
                    currency_holdings_list, operator.attrgetter('cost_currency'))

                holdings_list = [holding
                                 for holding in holdings_list
                                 if holding.currency and holding.cost_currency]

                # If after conversion there are no valid holdings, skip the currency
                # altogether.
                if holdings_list:
                    totals[currency] = holdings_list[0].market_value

            monthly_totals.append({
                'begin_date': begin_date,
                'end_date': end_date,
                'totals': totals
            })
        return monthly_totals

    def net_worth(self):
        monthly_totals = self._net_worth_in_periods()
        if monthly_totals:
            current = monthly_totals[-1]['totals']
        else:
            current = {}
        return {
            'net_worth': current,
            'monthly_totals': monthly_totals
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
        # Make sure the included source files are sorted, behind the main source file
        return [self.beancount_file_path] + sorted(filter(lambda x: x != self.beancount_file_path,
                    [os.path.join(os.path.dirname(self.beancount_file_path), filename) for filename in self.options['include']]
                ))

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
        return sorted(self.price_map.forward_pairs)

    def prices(self, base, quote):
        return prices.get_all_prices(self.price_map, "{}/{}".format(base, quote))

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
            return activity_by_account[0] if len(activity_by_account) == 1 else None
        else:
            # nb_entries_by_type
            entries_by_type = misc_utils.groupby(lambda entry: type(entry).__name__, self.entries)
            nb_entries_by_type = { name: len(entries) for name, entries in entries_by_type.items() }

            all_postings = [posting
                            for entry in self.entries
                            if isinstance(entry, Transaction)
                            for posting in entry.postings]

            # nb_postings_by_account
            postings_by_account = misc_utils.groupby(lambda posting: posting.account, all_postings)
            nb_postings_by_account = { key: len(postings) for key, postings in postings_by_account.items() }

            return {
                'entries_by_type':           nb_entries_by_type,
                'entries_by_type_total':     sum(nb_entries_by_type.values()),
                'postings_by_account':       nb_postings_by_account,
                'postings_by_account_total': sum(nb_postings_by_account.values()),
                'activity_by_account':       self._activity_by_account()
            }


    def is_valid_document(self, file_path):
        """Check if the given file_path is present in one of the
           Document entries or in a "statement"-metadata in a Transaction entry.

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
                if 'statement' in entry.meta and entry.meta['statement'] == file_path:
                    is_present = True

        return is_present

    def query(self, bql_query_string, numberify=False):
        return query.run_query(self.all_entries, self.options, bql_query_string, numberify=numberify)

    def _last_posting_for_account(self, account_name):
        """
        Returns the last posting for an account (ignores Close)
        """
        real_account = realization.get_or_create(self.all_root_account,
                                                 account_name)

        last_posting = realization.find_last_active_posting(real_account.txn_postings)

        if not isinstance(last_posting, Close):
            return last_posting

        postings = realization.get_postings(real_account)
        if len(postings) >= 2:
            return postings[-2]

        return None

    def is_account_uptodate(self, account_name, look_back_days=60):
        """
        green:  if the latest posting is a balance check that passed (i.e., known-good)
        red:    if the latest posting is a balance check that failed (i.e., known-bad)
        yellow: if the latest posting is not a balance check (i.e., unknown)
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

        return (date.today() - entry.date).days

    def account_open_metadata(self, account_name):
        real_account = realization.get_or_create(self.root_account, account_name)
        postings = realization.get_postings(real_account)
        for posting in postings:
            if isinstance(posting, Open):
                return posting.meta
        return {}
