import os
from datetime import date, timedelta

import bisect, re, collections

from beancount import loader
from beancount.reports import balance_reports
from beancount.reports import html_formatter
from beancount.reports import context
from beancount.utils import bisect_key
from beancount.core import realization, flags
from beancount.core import interpolate
from beancount.web.views import AllView
from beancount.parser import options
from beancount.core import compare
from beancount.core.number import ZERO
from beancount.core.data import Open, Close, Note, Document, Balance, TxnPosting, Transaction, Pad  # TODO implement missing
from beancount.core.account_types import get_account_sign
from beancount.reports import holdings_reports
from beancount.core import getters
from beancount.web.views import YearView, TagView
from beancount.ops import summarize, prices, holdings
from beancount.ops.holdings import Holding

# This really belongs in beancount:src/python/beancount/ops/holdings.py
def get_holding_from_position(lot, number, account=None, price_map=None, date=None):
    """Compute a Holding corresponding to the specified position 'pos'.

    :param lot: A Lot object.
    :param number: The number of units of 'lot' in the position.
    :param account: A str, the name of the account, or None if not needed.
    :param price_map: A dict of prices, as built by prices.build_price_map().
    :param date: A datetime.date instance, the date at which to price the
        holdings.  If left unspecified, we use the latest price information.

    :return: A Holding object.
    """
    if lot.cost is not None:
        # Get price information if we have a price_map.
        market_value = None
        if price_map is not None:
            base_quote = (lot.currency, lot.cost.currency)
            price_date, price_number = prices.get_price(price_map,
                                                        base_quote, date)
            if price_number is not None:
                market_value = number * price_number
        else:
            price_date, price_number = None, None

        return Holding(account,
                       number,
                       lot.currency,
                       lot.cost.number,
                       lot.cost.currency,
                       number * lot.cost.number,
                       market_value,
                       price_number,
                       price_date)
    else:
        return Holding(account,
                       number,
                       lot.currency,
                       None,
                       lot.currency,
                       number,
                       number,
                       None,
                       None)

def inventory_at_dates(entries, dates, transaction_predicate, posting_predicate):
    """Generator that yields the aggregate inventory at the specified dates.

    The inventory for a specified date includes all matching postings PRIOR to
    it.

    :param entries: list of entries, sorted by date.
    :param dates: iterator of dates
    :param transaction_predicate: predicate called on each Transaction entry to
        decide whether to include its postings in the inventory.
    :param posting_predicate: predicate with the Transaction and Posting to
        decide whether to include the posting in the inventory.
    """
    entry_i = 0
    num_entries = len(entries)

    # inventory maps lot to amount
    inventory = collections.defaultdict(lambda: ZERO)
    prev_date = None
    for date in dates:
        assert prev_date is None or date >= prev_date
        prev_date = date
        while entry_i < num_entries and entries[entry_i].date < date:
            entry = entries[entry_i]
            entry_i += 1
            if isinstance(entry, Transaction) and transaction_predicate(entry):
                for posting in entry.postings:
                    if posting_predicate(entry, posting):
                        old_value = inventory[posting.position.lot]
                        new_value = old_value + posting.position.number
                        if new_value == ZERO:
                            del inventory[posting.position.lot]
                        else:
                            inventory[posting.position.lot] = new_value
        yield inventory

def account_descendants_re_pattern(*roots):
    """Returns pattern for matching descendant accounts.

    :param roots: The list of parent account names.  These should not
        end with a ':'.

    :return: The regular expression pattern for matching descendants of
             the specified parents, or those parents themselves.
    """
    return '|'.join('(?:^' + re.escape(name) + '(?::|$))' for name in roots)

def holdings_at_dates(entries, dates, price_map, options_map):
    """Computes aggregate holdings at mulitple dates.

    Yields for each date the list of Holding objects.  The holdings are
    aggregated across accounts; the Holding objects will have the account field
    set to None.

    :param entries: The list of entries.
    :param dates: The list of dates.
    :param price_map: A dict of prices, as built by prices.build_price_map().
    :param options_map: The account options.
    """
    account_types = options.get_account_types(options_map)
    FLAG_UNREALIZED = flags.FLAG_UNREALIZED
    transaction_predicate = lambda e: e.flag != FLAG_UNREALIZED
    account_re = re.compile(account_descendants_re_pattern(
        account_types.assets,
        account_types.liabilities))
    posting_predicate = lambda e, p: account_re.match(p.account)
    for date, inventory in zip(dates,
                               inventory_at_dates(
                                   entries, dates,
                                   transaction_predicate = transaction_predicate,
                                   posting_predicate = posting_predicate)):
        yield [get_holding_from_position(lot, number, price_map=price_map, date=date)
               for lot, number in inventory.items()]

class BeancountReportAPI(object):
    """
    The rationale behind api.py is the following:

    One day there will be a new module in beancount.report that returns all (for
    beancount-web required) views as Python-dicts and -arrays, compatible with
    JSON (so no datetime, etc.). Right now beancount.report does return data to
    be displayed in a console, and HTML, and this (JSON) could be a third way of
    "rendering" the data. These methods should be highly optimized for performance
    and numerical correctness. If that one day really makes it's way into the
    beancount-repo, then api.py is redundant and will be removed.

    For the JSON-part: I want to keep all the returns in api.py JSON-serializeable
    (although they are called directly right now), because then, with very little
    overhead, beancount-web could run on an external server and call into a local
    bean-report.

    Right now api.py it is just a hacky placeholder for what could be in the future,
    and therefore I only tried to get the numbers required, and did not optimize
    for performance at all.
    """

    def __init__(self, beancount_file_path):
        super(BeancountReportAPI, self).__init__()
        self.beancount_file_path = beancount_file_path
        self.load_file()

    def load_file(self):
        """Load self.beancount_file_path and compute things that are independent
        of how the entries might be filtered later"""

        self.entries, self._errors, self.options = loader.load_file(self.beancount_file_path)
        self.all_entries = self.entries
        self.price_map = prices.build_price_map(self.all_entries)

        self.title = self.options['title']

        self.errors = []
        for error in self._errors:
            self.errors.append({
                'file': error.source['filename'],
                'line': error.source['lineno'],
                'error': error.message,
                'entry': error.entry  # TODO render entry
            })

        self.active_years = list(getters.get_active_years(self.all_entries))
        self.active_tags = list(getters.get_all_tags(self.all_entries))

        self.account_types = options.get_account_types(self.options)
        self.real_accounts = realization.realize(self.entries, self.account_types)
        self.all_accounts = self._account_components()

    def filter(self, year=None, tag=None):
        if year:
            yv = YearView(self.all_entries, self.options, str(year), year)
            self.entries = yv.entries

        if tag:
            tv = TagView(self.all_entries, self.options, tag, set([tag]))
            self.entries = tv.entries

        self.real_accounts = realization.realize(self.entries, self.account_types)

    def _account_components(self):
        # TODO rename
        """Gather all the account components available in the given directives.

        Args:
          entries: A list of directive instances.
        Returns:
            [
                {
                    'name': 'TV',
                    'full_name': 'Expenses:Tech:TV',
                    'depth': 3
                }, ...
            ]
        """
        accounts = []
        for child_account in realization.iter_children(self.real_accounts):
            accounts.append({
                'name': child_account.account.split(':')[-1],
                'full_name': child_account.account,
                'depth': child_account.account.count(':')+1,
            })

        return accounts[1:]

    def _table_tree(self, real_accounts):
        """
        Renders real_accounts and it's children as a flat list to be used
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

        # FIXME this does not seem correct
        if isinstance(real_accounts, None.__class__):
            return []

        lines = []
        for real_account in realization.iter_children(real_accounts):

            line = {
                'account': real_account.account,
                'balances_children': self._table_totals(real_account),
                'balances': {},
                'is_leaf': (len(list(realization.iter_children(real_account))) == 1), # True if the accoutn has no children or has entries
                'postings_count': len(real_account.txn_postings)
            }

            for pos in real_account.balance.cost():
                line['balances'][pos.lot.currency] = pos.number

            # Accounts that are not leafs but have entries are leafs as well
            for currency in self.options['commodities']:
                if currency in line['balances'] and currency in line['balances_children']:
                    if line['balances'][currency] != line['balances_children'][currency]:
                        line['is_leaf'] = True

            lines.append(line)

        return lines

    def _table_totals(self, real_accounts):
        """
            Renders the total balances for root_acccounts and their children.

            Returns:
                {
                    'USD': 123.45,
                    ...
                }
        """

        totals = {}

        # FIXME This sometimes happens when called from self.account(...)
        #       and there is no entry in that specific month. This also produces
        #       a missing bar in the bar chart.
        if isinstance(real_accounts, None.__class__):
            return {}

        for real_account in realization.iter_children(real_accounts):
            for pos in real_account.balance.cost():
                if not pos.lot.currency in totals:
                    totals[pos.lot.currency] = ZERO
                totals[pos.lot.currency] += pos.number

        return totals

    def _inventory_to_json(self, inventory):
        """
        Renders an Inventory to a currency -> amount dict.

        Returns:
            {
                'USD': 123.45,
                'CAD': 567.89,
                ...
            }
        """
        result = collections.defaultdict(lambda: ZERO)
        for position in inventory:
            result[position.lot.currency] += position.number
        return { currency: number for currency, number in result.items() if number != ZERO }

    def _journal_for_postings(self, postings, include_types=None):
        journal = []

        for posting, leg_postings, change, entry_balance in realization.iterate_with_balance(postings):

            if include_types and not isinstance(posting, include_types):
                continue

            if  isinstance(posting, Transaction) or \
                isinstance(posting, Note) or \
                isinstance(posting, Balance) or \
                isinstance(posting, Open) or \
                isinstance(posting, Close) or \
                isinstance(posting, Pad) or \
                isinstance(posting, Document):   # TEMP

                # if isinstance(posting, TxnPosting):
                #     posting = posting.txn

                entry = {
                    'meta': {
                        'type': posting.__class__.__name__.lower(),
                        'filename': posting.meta['filename'],
                        'lineno': posting.meta['lineno']
                    },
                    'date': posting.date,
                    'hash': compare.hash_entry(posting)
                }

                if isinstance(posting, Open):
                    entry['account'] =       posting.account
                    entry['currencies'] =    posting.currencies
                    entry['booking'] =       posting.booking # TODO im html-template

                if isinstance(posting, Close):
                    entry['account'] =       posting.account

                if isinstance(posting, Note):
                    entry['comment'] =       posting.comment

                if isinstance(posting, Document):
                    entry['account'] =       posting.account
                    entry['filename'] =      posting.filename

                if isinstance(posting, Pad):
                    entry['account'] =       posting.account
                    entry['source_account'] =      posting.source_account

                if isinstance(posting, Balance):
                    # TODO failed balances
                    entry['account'] =       posting.account
                    entry['change'] =        { posting.amount.currency: posting.amount.number }
                    entry['balance'] =       { posting.amount.currency: posting.amount.number }
                    entry['tolerance'] =     posting.tolerance  # TODO currency? TODO in HTML-template
                    if posting.diff_amount:
                        entry['diff_amount'] =          posting.diff_amount.number  # TODO in HTML-template
                        entry['diff_amount_currency'] = posting.diff_amount.currency  # TODO in HTML-template

                if isinstance(posting, Transaction):
                    if posting.flag == 'P':
                        entry['meta']['type'] = 'padding'

                    entry['flag'] =         posting.flag
                    entry['payee'] =        posting.payee
                    entry['narration'] =    posting.narration
                    entry['tags'] =         posting.tags
                    entry['links'] =        posting.links
                    entry['change'] =       self._inventory_to_json(change)
                    entry['balance'] =      self._inventory_to_json(entry_balance)
                    entry['legs'] =         []

                    for posting_ in posting.postings:
                        leg = {
                            'account': posting_.account,
                            'flag': posting_.flag,
                            'hash': entry['hash']
                        }

                        if posting_.position:
                            leg['position'] = posting_.position.number
                            leg['position_currency'] = posting_.position.lot.currency

                        if posting_.price:
                            leg['price'] = posting_.price.number
                            leg['price_currency'] = posting_.price.currency

                        entry['legs'].append(leg)


                journal.append(entry)

        return journal

    def _month_tuples(self, entries):
        """
        Calculates tuples of (month_begin, month_end) for the period in
        which entries contains Transactions.

        Returns:
            [
                (begin_date, end_date),
                ...
            ]
        """
        date_first, date_last = getters.get_min_max_dates(entries, (Transaction))

        def get_next_month(date_):
            month = (date_.month % 12) + 1
            year = date_.year + (date_.month + 1 > 12)
            return date(year, month, 1)

        date_first = date(date_first.year, date_first.month, 1)
        date_last = get_next_month(date_last) - timedelta(days=1)

        month_tuples = []
        while date_first <= date_last:
            month_tuples.append((date_first, get_next_month(date_first) - timedelta(days=1)))
            date_first = get_next_month(date_first)

        return month_tuples


    def monthly_income_expenses_totals(self):
        month_tuples = self._month_tuples(self.entries)
        monthly_totals = []
        for begin_date, end_date in month_tuples:
            entries = self._entries_in_inclusive_range(begin_date, end_date)
            realized = realization.realize(entries, self.account_types)
            income_totals = self._table_totals(realization.get(realized, self.account_types.income))
            expenses_totals = self._table_totals(realization.get(realized, self.account_types.expenses))

            # FIXME find better way to only include relevant totals (lots of ZERO-ones at the beginning)
            sum_ = ZERO
            for currency, number in income_totals.items():
                sum_ += number
            for currency, number in expenses_totals.items():
                sum_ += number

            if sum_ != ZERO:
                monthly_totals.append({
                    'begin_date': begin_date,
                    'end_date': end_date,
                    'income_totals': income_totals,
                    'expenses_totals': expenses_totals
                })

        return monthly_totals

    def _monthly_totals(self, account_name, entries):
        """
        Renders totals for the active months in the entries

        Returns:
          [
              {
                  'begin_date': Date(...),    # TODO rename to date_begin
                  'end_date':   Date(...),    # TODO rename to date_end
                  'totals':     {
                                    'USD': 123.45,
                                }
              }, ...
          ]
        """

        month_tuples = self._month_tuples(self.entries)
        monthly_totals = []
        for begin_date, end_date in month_tuples:
            totals = self.balances_totals(account_name, begin_date=begin_date, end_date=end_date)

            # FIXME find better way to only include relevant totals (lots of ZERO-ones at the beginning)
            sum_ = 0
            for currency, number in totals.items():
                sum_ += number

            if sum_ != 0:
                monthly_totals.append({
                    'begin_date': begin_date,
                    'end_date': end_date,
                    'totals': totals
                })

        return monthly_totals

    def _entries_in_inclusive_range(self, begin_date=None, end_date=None):
        """
        Returns the list of entries satisfying begin_date <= date <= end_date.
        """
        get_date = lambda x: x.date
        if begin_date is None:
            begin_index = 0
        else:
            begin_index = bisect_key.bisect_left_with_key(self.entries, begin_date, key=get_date)
        if end_date is None:
            end_index = len(self.entries)
        else:
            end_index = bisect_key.bisect_left_with_key(self.entries, end_date+timedelta(days=1), key=get_date)
        return self.entries[begin_index:end_index]

    def _real_accounts(self, account_name, begin_date=None, end_date=None):
        """
        Returns the realization.RealAccount instances for account_name, and
        their entries clamped by the optional begin_date and end_date.

        Warning: For efficiency, the returned result does not include any added
        postings to account for balances at 'begin_date'.

        :return: realization.RealAccount instances
        """
        entries = self._entries_in_inclusive_range(begin_date=begin_date, end_date=end_date)
        real_accounts = realization.get(realization.realize(entries, self.account_types), account_name)

        return real_accounts


    def balances(self, account_name, begin_date=None, end_date=None):
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
        real_accounts = self._real_accounts(account_name, begin_date, end_date)

        return self._table_tree(real_accounts)

    def balances_totals(self, account_name, begin_date=None, end_date=None):
        """
        Renders account_name and it's children as a flat list to be used
        in rendering tables.

        Returns:
            {
               'USD': 123.45,
            }
        """
        real_accounts = self._real_accounts(account_name, begin_date, end_date)

        return self._table_totals(real_accounts)

    def monthly_balances(self, account_name):
        # TODO include balances_children
        # the account tree at time now

        account_names = [account['full_name'] for account in self._account_components() if account['full_name'].startswith(account_name)]

        month_tuples = self._month_tuples(self.entries)
        monthly_totals = { end_date.isoformat(): { currency: ZERO for currency in self.options['commodities']} for begin_date, end_date in month_tuples }

        arr = { account_name: {} for account_name in account_names }

        for begin_date, end_date in month_tuples:
            real_accounts = self._real_accounts(account_name, begin_date=begin_date, end_date=end_date)

            _table_tree = self._table_tree(real_accounts)
            for line in _table_tree:
                arr[line['account']][end_date.isoformat()] = {
                    'balances': line['balances'],
                    'balances_children': line['balances_children']
                }

                if line['postings_count'] > 0:
                    for currency, number in line['balances'].items():
                        monthly_totals[end_date.isoformat()][currency] += number

        balances = sorted([
                        { 'account': account, 'totals': totals } for account, totals in arr.items()
                      ], key=lambda x: x['account'])

        return {
            'months': [end_date for begin_date, end_date in month_tuples],
            'balances': balances,
            'totals': monthly_totals
        }

    def trial_balance(self):
        return self._table_tree(self.real_accounts)[1:]

    def journal(self, account_name=None):
        if account_name:
            real_account = realization.get(self.real_accounts, account_name)
        else:
            real_account = self.real_accounts

        postings = realization.get_postings(real_account)
        return self._journal_for_postings(postings)

    def documents(self):
        postings = realization.get_postings(self.real_accounts)
        return self._journal_for_postings(postings, Document)

    def notes(self):
        postings = realization.get_postings(self.real_accounts)
        return self._journal_for_postings(postings, Note)

    def holdings(self):
        return holdings_reports.report_holdings(None, False, self.entries, self.options)

    def _net_worth_in_periods(self):
        month_tuples = self._month_tuples(self.entries)
        monthly_totals = []
        end_dates = [p[1] + timedelta(days=1) for p in month_tuples]

        for (begin_date, end_date), holdings_list in zip(month_tuples,
                                                        holdings_at_dates(entries=self.entries,
                                                                          dates=end_dates,
                                                                          options_map=self.options,
                                                                          price_map=self.price_map)):
            totals = dict()
            for currency in self.options['operating_currency']:
                total = ZERO
                for holding in holdings.convert_to_currency(self.price_map, currency, holdings_list):
                    if holding.cost_currency == currency and holding.market_value:
                        total += holding.market_value
                if total != ZERO:
                    totals[currency] = total

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

    def context(self, ehash=None):
        matching_entries = [entry
                                for entry in self.entries
                                if ehash == compare.hash_entry(entry)]

        contexts = []
        dcontext = self.options['dcontext']

        for entry in matching_entries:
            context_str = context.render_entry_context(
                self.entries, self.options, entry)

            hash_ = context_str.split("\n",2)[0].split(':')[1].strip()
            filenamelineno = context_str.split("\n",2)[1]
            filename = filenamelineno.split(":")[1].strip()
            lineno = int(filenamelineno.split(":")[2].strip())

            contexts.append({
                'hash': hash_,
                'context': context_str.split("\n",2)[2],
                'filename': filename,
                'line': lineno
            })

        # TODO
        #        if len(matching_entries) == 0:
        #            print("ERROR: Could not find matching entry for '{}'".format(ehash),
        #                  file=oss)
        #
        #        elif len(matching_entries) > 1:
        #            print("ERROR: Ambiguous entries for '{}'".format(ehash),
        #                  file=oss)
        #            print(file=oss)
        #            dcontext = app.options['dcontext']
        #            printer.print_entries(matching_entries, dcontext, file=oss)
        #
        #        else:

        return {
            'hash': ehash,
            'contexts': contexts,
            'journal': self._journal_for_postings(matching_entries)
        }

    def treemap_data(self, account_name):
        return {
            'label': account_name,
            'balances': self.balances(account_name),
            'modifier': get_account_sign(account_name, self.account_types),
        }

    def source_files(self):
        return list(set(
                        [self.beancount_file_path]
                        + [os.path.join(os.path.dirname(self.beancount_file_path), filename) for filename in self.options['include']]
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

    def monthly_totals(self, account_name):
        real_account = realization.get(self.real_accounts, account_name)
        return self._monthly_totals(real_account.account, self.entries)
