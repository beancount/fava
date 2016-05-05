from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from beancount.core.data import Custom

from fava.util.date import days_in_daterange, number_of_days_in_period

class Budgets(object):

    def __init__(self, entries):
        """
        Reads budget directives from the specified list of beancount entries.

        Example for a budget directive:

            2015-04-09 custom "budget" Expenses:Books "monthly"  20.00 EUR
        """
        self.datelines = {}
        self.currencies = set()

        for entry in entries:
            if isinstance(entry, Custom) and entry.type == 'budget':
                account_name = entry.values[0].value

                if account_name not in self.datelines:
                    self.datelines[account_name] = []

                self.datelines[account_name].append(
                    Dateline(date_start=entry.date,
                             period=entry.values[1].value,
                             number=entry.values[2].value.number,
                             currency=entry.values[2].value.currency)
                )

                self.currencies.add(entry.values[2].value.currency)

        for name, account in self.datelines.items():
            self.datelines[name] = sorted(self.datelines[name],
                                          key=lambda
                                          dateline: dateline.date_start)

    def _matching_dateline(self, datelines, date_active):
        """Returns the dateline that is active on the specifed date."""
        last_seen_dateline = None
        for dateline in datelines:
            if dateline.date_start <= date_active:
                last_seen_dateline = dateline
            else:
                break
        return last_seen_dateline

    def budget(self, account_name, date_from, date_to):
        """
        Returns a dictionary (currency => number) with the budget for the
        specified account and period.
        """
        currency_dict = defaultdict(lambda: Decimal(0.0))

        if account_name not in self.datelines.keys():
            return currency_dict

        for single_day in days_in_daterange(date_from, date_to):
            dateline = self._matching_dateline(
                self.datelines[account_name], single_day)
            if dateline:
                currency_dict[dateline.currency] += dateline.value(single_day)

        return currency_dict


class Dateline(object):

    def __init__(self, date_start, period, number, currency):
        super(Dateline, self).__init__()
        self.date_start = date_start
        self.period = period.lower()
        self.number = number
        self.currency = currency

    def value(self, date_):
        return self.number / number_of_days_in_period(self.period, date_)

    def __repr__(self):
        return "Dateline ({}, {}, {}, {})" \
            .format(self.date_start, self.period, self.number, self.currency)
