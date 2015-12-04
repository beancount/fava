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
from beancount.core.data import Open, Close, Note, Document, Balance, TxnPosting, Transaction, Pad  # TODO fehlende implementieren
from beancount.reports import holdings_reports
from beancount.core import getters
from beancount.web.views import YearView, TagView
from beancount.ops import summarize


class BeancountReportAPI(object):
    """docstring for BeancountReportAPI"""

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

    def _table_tree(self, root_accounts):
        lines = []

        for real_account in realization.dump(root_accounts):
            line_data = real_account[2]

            line = {
                'account': line_data.account,
                'operating_balances': { currency: None for currency in self.options_map['operating_currency']},
                'other_balances': {}
            }

            for pos in line_data.balance.cost():
                if pos.lot.currency in self.options_map['operating_currency']:
                    line['operating_balances'][pos.lot.currency] = pos.number
                else:
                    line['other_balances'][pos.lot.currency] = pos.number

            lines.append(line)

        return lines

    def _table_totals(self, root_accounts):
        totals = {
            'operating_totals': { currency: ZERO for currency in self.options_map['operating_currency']},
            'other_totals': {}
        }

        for real_account in realization.dump(root_accounts):
            line_data = real_account[2]

            for pos in line_data.balance.cost():
                if pos.lot.currency in self.options_map['operating_currency']:
                    totals['operating_totals'][pos.lot.currency] += pos.number
                else:
                    if pos.lot.currency in totals['other_totals']:
                        totals['other_totals'][pos.lot.currency] += pos.number
                    else:
                        totals['other_totals'][pos.lot.currency] = pos.number

        return totals

    def _inventory_to_json(self, inventory):
        json = []

        for position in sorted(inventory):
            json.append({
                'number':   position.number,
                'currency': position.lot.currency
            })

        return json

    def _process_postings(self, postings):
        jrnl = []

        #for posting in postings:
        i = 1
        for posting, leg_postings, change, entry_balance in realization.iterate_with_balance(postings):

            # print(change, change.__class__)
            # print("Balance: ", entry_balance)
            # print()
            i += 1

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
                        'filename': posting.meta.filename,
                        'lineno': posting.meta.lineno
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
                    entry['currencies'] =    posting.currencies
                    entry['booking'] =       posting.booking # TODO im html-template

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
                    entry['meta']['type'] = 'balance'
                    entry['account'] =       posting.account
                    entry['change'] =        [
                                                {
                                                    'number':     posting.amount.number,
                                                    'currency':   posting.amount.currency
                                                }
                                             ]
                    entry['balance'] =        self._inventory_to_json(entry_balance)
                    entry['tolerance'] =     posting.tolerance  # TODO währung? TODO im html-template
                    entry['diff_amount'] =     posting.diff_amount  # TODO währung? TODO im html-template

                if isinstance(posting, Transaction):
                    if posting.flag == 'P':
                        entry['meta']['type'] = 'padding'
                    else:
                        entry['meta']['type'] = 'transaction'

                    entry['flag'] =       posting.flag
                    entry['payee'] =      posting.payee
                    entry['narration'] =      posting.narration
                    entry['tags'] =      posting.tags
                    entry['links'] =      posting.links
                    entry['change']         = self._inventory_to_json(change)
                    entry['balance']         = self._inventory_to_json(entry_balance)
                    entry['legs'] = []


                    for posting_ in posting.postings:
                        leg = {
                            'account': posting_.account,
                            'flag': posting_.flag,
                            # 'meta': {
                            #     'filename': posting_.meta.filename,
                            #     'lineno': posting_.meta.lineno
                            # }
                        }

                        if posting_.position:
                            leg['position'] = posting_.position.number
                            leg['position_currency'] = posting_.position.lot.currency

                        if posting_.price:
                            leg['price'] = posting_.price.number
                            leg['price_currency'] = posting_.price.currency

                        entry['legs'].append(leg)


                jrnl.append(entry)

        return jrnl

    def _get_month_tuples(self, entries):
        date_first, date_last = getters.get_min_max_dates(entries, (Transaction))

        def get_next_month(datee):
            month = (datee.month % 12) + 1
            year = datee.year + (datee.month + 1 > 12)
            return date(year, month, 1)

        date_first = date(date_first.year, date_first.month, 1)
        date_last = get_next_month(date_last) - timedelta(days=1)

        month_tuples = []
        while date_first <= date_last:
            month_tuples.append((date_first, get_next_month(date_first) - timedelta(days=1)))
            date_first = get_next_month(date_first)

        return month_tuples

    def _get_monthly_totals(self, entries):
        month_tuples = self._get_month_tuples(self.entries)
        monthly_totals = []
        for begin_date, end_date in month_tuples:
            entries, index = summarize.clamp_opt(self.entries, begin_date, end_date,
                                                          self.options_map)
            monthly_totals.append({
                'begin_date': begin_date,
                'end_date': end_date,
                'operating_currencies': self.options_map['operating_currency'],
                'income_totals': self._table_totals(realization.get(realization.realize(entries, self.account_types), self.options_map['name_income'])),
                'expenses_totals': self._table_totals(realization.get(realization.realize(entries, self.account_types), self.options_map['name_expenses']))
            })

        return {
            'operating_currencies': self.options_map['operating_currency'],
            'totals': monthly_totals
        }


    def balance_sheet(self, timespan=None, components=None, tags=None):
        return {
            'assets':             self._table_tree(realization.get(self.real_accounts, self.options_map['name_assets'])),
            'assets_totals':      self._table_totals(realization.get(self.real_accounts, self.options_map['name_assets'])),
            'liabilities':        self._table_tree(realization.get(self.real_accounts, self.options_map['name_liabilities'])),
            'liabilities_totals': self._table_totals(realization.get(self.real_accounts, self.options_map['name_liabilities'])),
            'equity':             self._table_tree(realization.get(self.real_accounts, self.options_map['name_equity'])),
            'equity_totals':      self._table_totals(realization.get(self.real_accounts, self.options_map['name_equity'])),
            'currencies':         self.options_map['operating_currency'] + [ 'Other' ],
            'monthly_totals':     self._get_monthly_totals(self.entries)
        }

        # aex='account ~ "Expenses"'
        # alo='account ~ "Liabilities:Loans"'
        # ain='account ~ "Income"'


    def income_statement(self, timespan=None, components=None, tags=None):
        return {
            'income':             self._table_tree(realization.get(self.real_accounts, self.options_map['name_income'])),
            'income_totals':      self._table_totals(realization.get(self.real_accounts, self.options_map['name_income'])),
            'expenses':        self._table_tree(realization.get(self.real_accounts, self.options_map['name_expenses'])),
            'expenses_totals': self._table_totals(realization.get(self.real_accounts, self.options_map['name_expenses'])),
            'currencies':         self.options_map['operating_currency'] + [ 'Other' ],
            'monthly_totals':     self._get_monthly_totals(self.entries)
        }

    def trial_balance(self, timespan=None, components=None, tags=None):
        return {
            'positions':  self._table_tree(self.real_accounts),
            'currencies': self.options_map['operating_currency'] + [ 'Other' ]
        }

    def errors(self):
        errors = []

        for error in self._errors:
            errors.append({
                'file': error.source.filename,
                'line': error.source.lineno,
                'error': error.message,
                'entry': error.entry  # TODO render entry
            })

        return errors

    def journal(self, account_name=None, timespan=None, tags=None):
        journal = []

        postings = realization.get_postings(self.real_accounts)
        journal = self._process_postings(postings)

        return journal

    def documents(self, account_name=None, timespan=None, tags=None):
        documents = []

        postings = realization.get_postings(self.real_accounts)

        for posting in postings:
            if isinstance(posting, Document):
                documents.append({
                    'meta': {
                        'type': 'document',
                        'filename': posting.meta['filename'],
                        'lineno': posting.meta['lineno']
                    },
                    'date': posting.date,
                    'account': posting.account,
                    'filename': posting.filename
                })

        return documents

    def title(self):
        return self.options_map['title']

    def holdings(self):
        return holdings_reports.report_holdings(None, False, self.entries, self.options_map)

    def net_worth(self):
        networthtable = holdings_reports.NetWorthReport(None, None)

        return networthtable.generate_table(self.entries, self.errors, self.options_map)

    def context(self, ehash=None):
        matching_entries = [entry
                                for entry in self.entries
                                if ehash == compare.hash_entry(entry)]


    def active_years(self):
        return list(getters.get_active_years(self.all_entries))

    def active_tags(self):
        return list(getters.get_all_tags(self.all_entries))

    def _my_get_account_components(self, entries):
        """Gather all the account components available in the given directives.

        Args:
          entries: A list of directive instances.
        Returns:
          A set of strings, the unique account components, including the root
          account names.
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

    def active_components(self):
        return self._my_get_account_components(self.all_entries)
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

        content = ""

        dcontext = self.options_map['dcontext']
        for entry in matching_entries:
            content += context.render_entry_context(
                self.entries, self.options_map, dcontext,
                entry.meta["filename"], entry.meta["lineno"])

        return {
            'hash': ehash,
            'context': content
        }

    def source(self):
        return self._source

    def account(self, name=None, timespan=None, tags=None):
        journal = []

        real_account = realization.get(self.real_accounts, name)
        postings = realization.get_postings(real_account)
        journal = self._process_postings(postings)

        return {
            'name': name,
            'journal': journal
        }


