from datetime import date, timedelta

from beancount import loader
from beancount.reports import balance_reports
from beancount.reports import html_formatter
from beancount.reports import context
from beancount.core import realization
from beancount.core import interpolate
from beancount.web.views import AllView
from beancount.parser import options
from beancount.core import compare
from beancount.core.number import ZERO
from beancount.core.data import Open, Close, Note, Document, Balance, TxnPosting, Transaction, Pad  # TODO implement missing
from beancount.reports import holdings_reports
from beancount.core import getters
from beancount.web.views import YearView, TagView
from beancount.ops import summarize


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
        self.reload()

    def reload(self, year=None, tag=None):
        with open(self.beancount_file_path, encoding='utf8') as f:
            self._source = f.read()

        self.entries, self._errors, self.options_map = loader.load_file(self.beancount_file_path)
        self.all_entries = self.entries

        if year:
            yv = YearView(self.all_entries, self.options_map, str(year), year)
            self.entries = yv.entries

        if tag:
            tv = TagView(self.all_entries, self.options_map, tag, set([tag]))
            self.entries = tv.entries

        self.account_types = options.get_account_types(self.options_map)
        # self.allview = AllView(self.entries, self.options_map, 'TEST')
        self.real_accounts = realization.realize(self.entries, self.account_types)

    def _account_components(self, entries):
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
        accounts = realization.dump(self.real_accounts)  # self.real_accounts  # getters.get_accounts(entries)
        components = []
        for real_account in accounts:
            line_data = real_account[2]
            account_name = line_data.account

            components.append({
                'name': account_name.split(':')[-1],
                'full_name': account_name,
                'depth': len(account_name.split(':'))
            })

        return components

    def _account_level(self, account_name):
        """
        The sublevel at which an account is. Eg. "Exenses:IT" is level 2, "Expenses:IT:Internet" is level 3

        Returns:
            The sublevel at which an account is.
        """
        return account_name.count(":")+1

    def _table_tree(self, root_accounts):
        """
        Renders root_accounts and it's children as a flat list to be used
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
        lines = []

        for real_account in realization.dump(root_accounts):
            real_account = real_account[2]

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
            for currency in self.options_map['commodities']:
                if currency in line['balances'] and currency in line['balances_children']:
                    if line['balances'][currency] != line['balances_children'][currency]:
                        line['is_leaf'] = True

            lines.append(line)

        return lines

    def _table_totals(self, root_accounts):
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
        if isinstance(root_accounts, None.__class__):
            return {}

        for real_account in realization.dump(root_accounts):
            for pos in real_account[2].balance.cost():
                if not pos.lot.currency in totals:
                    totals[pos.lot.currency] = ZERO
                totals[pos.lot.currency] += pos.number

        return totals

    def _inventory_to_json(self, inventory):
        """
        Renders an Inventory to an array.

        Returns:
            [
                {
                    'number': 123.45,
                    'currency': 'USD'
                }, ...
            ]
        """
        return { position.lot.currency: position.number for position in sorted(inventory) }

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
                        'filename': posting.meta['filename'],
                        'lineno': posting.meta['lineno']
                    },
                    'date': posting.date,
                    'hash': compare.hash_entry(posting)
                }

                if isinstance(posting, Open):
                    entry['meta']['type'] = 'open'
                    entry['account'] =       posting.account
                    entry['currencies'] =    posting.currencies
                    entry['booking'] =       posting.booking # TODO im html-template

                if isinstance(posting, Close):
                    entry['meta']['type'] = 'close'
                    entry['account'] =       posting.account

                if isinstance(posting, Note):
                    entry['meta']['type'] = 'note'
                    entry['comment'] =       posting.comment

                if isinstance(posting, Document):
                    entry['meta']['type'] = 'document'
                    entry['account'] =       posting.account
                    entry['filename'] =      posting.filename

                if isinstance(posting, Pad):
                    entry['meta']['type'] = 'pad'
                    entry['account'] =       posting.account
                    entry['source_account'] =      posting.source_account

                if isinstance(posting, Balance):
                    # TODO failed balances
                    entry['meta']['type'] = 'balance'
                    entry['account'] =       posting.account
                    entry['change'] =        { posting.amount.currency: posting.amount.number }
                    entry['balance'] =       { posting.amount.currency: posting.amount.number }
                    entry['tolerance'] =     posting.tolerance  # TODO currency? TODO in HTML-template
                    entry['diff_amount'] =   posting.diff_amount  # TODO currency? TODO in HTML-template

                if isinstance(posting, Transaction):
                    if posting.flag == 'P':
                        entry['meta']['type'] = 'padding'
                    else:
                        entry['meta']['type'] = 'transaction'

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

    # TODO rendundant
    def _get_monthly_ie_totals(self, entries):
        """
        Renders TODO
        """

        month_tuples = self._month_tuples(entries)
        monthly_totals = []
        for begin_date, end_date in month_tuples:
            entries, index = summarize.clamp_opt(self.entries, begin_date, end_date + timedelta(days=1),
                                                          self.options_map)

            income_totals = self._table_totals(realization.get(realization.realize(entries, self.account_types), self.options_map['name_income']))
            expenses_totals = self._table_totals(realization.get(realization.realize(entries, self.account_types), self.options_map['name_expenses']))

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


    def balance_sheet(self, timespan=None, components=None, tags=None):
        return {
            'assets':             self.balances(self.options_map['name_assets']),
            'assets_totals':      self.balances_totals(self.options_map['name_assets']),
            'liabilities':        self.balances(self.options_map['name_liabilities']),
            'liabilities_totals': self.balances_totals(self.options_map['name_liabilities']),
            'equity':             self.balances(self.options_map['name_equity']),
            'equity_totals':      self.balances_totals(self.options_map['name_equity']),
            'monthly_totals':     self._get_monthly_ie_totals(self.entries)
        }

    def income_statement(self, timespan=None, components=None, tags=None):
        return {
            'income':             self.balances(self.options_map['name_income']),
            'income_totals':      self.balances_totals(self.options_map['name_income']),
            'expenses':           self.balances(self.options_map['name_expenses']),
            'expenses_totals':    self.balances_totals(self.options_map['name_expenses']),
            'monthly_totals':     self._get_monthly_ie_totals(self.entries)
        }

    def _real_accounts(self, account_name, begin_date=None, end_date=None):
        """
        Returns the realization.RealAccount instances for account_name, and their entries
        clamped by the optional begin_date and end_date.

        Returns:
            realization.RealAccount instances
        """
        begin_date_, end_date_ = getters.get_min_max_dates(self.entries, (Transaction))
        if begin_date:
            begin_date_ = begin_date
        if end_date:
            end_date_ = end_date

        entries, index = summarize.clamp_opt(self.entries, begin_date_, end_date_ + timedelta(days=1),
                                                     self.options_map)

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

        account_names = [account['full_name'] for account in self._account_components(self.entries) if account['full_name'].startswith(account_name)]

        month_tuples = self._month_tuples(self.entries)
        monthly_totals = { end_date.isoformat(): { currency: ZERO for currency in self.options_map['commodities']} for begin_date, end_date in month_tuples }

        arr = { account_name: {} for account_name in account_names }

        for begin_date, end_date in month_tuples:
            root_accounts = self._real_accounts(account_name, begin_date=begin_date, end_date=end_date)

            _table_tree = self._table_tree(root_accounts)
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

    def trial_balance(self, timespan=None, components=None, tags=None):
        return self._table_tree(self.real_accounts)

    def errors(self):
        errors = []

        for error in self._errors:
            errors.append({
                'file': error.source['filename'],
                'line': error.source['lineno'],
                'error': error.message,
                'entry': error.entry  # TODO render entry
            })

        return errors

    def journal(self, account_name=None, timespan=None, tags=None):
        postings = realization.get_postings(self.real_accounts)
        return self._journal_for_postings(postings)

    def documents(self, account_name=None, timespan=None, tags=None):
        postings = realization.get_postings(self.real_accounts)
        return self._journal_for_postings(postings, Document)

    def title(self):
        return self.options_map['title']

    def holdings(self):
        return holdings_reports.report_holdings(None, False, self.entries, self.options_map)

    def _net_worth_in_periods(self):
        month_tuples = self._month_tuples(self.entries)
        monthly_totals = []
        date_start = month_tuples[0][0]
        networthtable = holdings_reports.NetWorthReport(None, None)

        for begin_date, end_date in month_tuples:
            entries, index = summarize.clamp_opt(self.entries, date_start, end_date + timedelta(days=1),
                                                          self.options_map)

            networth_as_table = networthtable.generate_table(entries, self.errors, self.options_map)

            totals = dict(networth_as_table[2])
            for key, value in totals.items():
                totals[key] = float(value.replace(',', ''))

            monthly_totals.append({
                'begin_date': begin_date,
                'end_date': end_date,
                'totals': totals
            })

        return monthly_totals

    def net_worth(self):
        networth_report = holdings_reports.NetWorthReport(None, None)
        networth_as_table = networth_report.generate_table(self.entries, self.errors, self.options_map)

        current_net_worth = dict(networth_as_table[2])
        for key, value in current_net_worth.items():
            current_net_worth[key] = float(value.replace(',', ''))

        return {
            'net_worth': current_net_worth,
            'monthly_totals': self._net_worth_in_periods()
        }

    def context(self, ehash=None):
        matching_entries = [entry
                                for entry in self.entries
                                if ehash == compare.hash_entry(entry)]

        contexts = []
        dcontext = self.options_map['dcontext']

        for entry in matching_entries:
            context_str = context.render_entry_context(
                self.entries, self.options_map, dcontext,
                entry.meta["filename"], entry.meta["lineno"])

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

    def active_years(self):
        return list(getters.get_active_years(self.all_entries))

    def active_tags(self):
        return list(getters.get_all_tags(self.all_entries))

    def active_components(self):
        # TODO rename?
        return self._account_components(self.all_entries)

    def source(self):
        return self._source

    def account(self, account_name=None, timespan=None, tags=None):
        real_account = realization.get(self.real_accounts, account_name)
        postings = realization.get_postings(real_account)
        monthly_totals = self._monthly_totals(real_account.account, self.entries)

        return {
            'name': account_name,
            'journal': self._journal_for_postings(postings),
            'monthly_totals': monthly_totals
        }

    def options(self):
        return self.options_map
