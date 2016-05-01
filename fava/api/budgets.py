from dateutil.relativedelta import relativedelta

from beancount.core.amount import Amount
from beancount.core.data import Custom
from beancount.core.inventory import Inventory

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
                             value=entry.values[2].value.number,
                             currency=entry.values[2].value.currency)
                )

                self.currencies.add(entry.values[2].value.currency)

        for name, account in self.datelines.items():
            self.datelines[name] = sorted(self.datelines[name],
                                          key=lambda
                                          dateline: dateline.date_start)

    def _daterange(self, start_date, end_date):
        """Yields a datetime instance for every day in the specified interval."""
        for n in range(int((end_date - start_date).days)):
            yield start_date + relativedelta(days=n)

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
        Returns a beancount.core.inventory.Inventory with the budget for the
        specified account and period.
        """
        inventory = Inventory()

        if not account_name in self.datelines.keys():
            return inventory

        for single_day in self._daterange(date_from, date_to):
            matching_dateline = self._matching_dateline(
                self.datelines[account_name], single_day)

            if matching_dateline:
                inventory.add_amount(Amount(
                    matching_dateline.value / matching_dateline.days,
                    matching_dateline.currency
                ))

        return inventory


class Dateline(object):

    def __init__(self, date_start, period, value, currency):
        super(Dateline, self).__init__()
        self.date_start = date_start
        self.period = period
        self.value = value
        self.currency = currency

        self.days = self._days(self.date_start, self.period)

    def _days(self, start_date, period):
        # TODO test this extensively, may be buggy
        period = period.lower()

        if period == 'daily':
            return 1
        if period == 'weekly':
            return 7
        if period == 'monthly':
            return ((start_date + relativedelta(months=1)) - start_date).days
        if period == 'quarterly':
            return ((start_date + relativedelta(months=3)) - start_date).days
        if period == 'yearly':
            return ((start_date + relativedelta(years=1)) - start_date).days
        raise Exception("Period unknown: {}".format(period))

    def __repr__(self):
        return "Dateline ({}, {}, {}, {})" \
            .format(self.date_start, self.period, self.value, self.currency)
