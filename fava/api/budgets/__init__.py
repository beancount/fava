import os
import sys
from datetime import datetime

from dateutil.relativedelta import relativedelta

class Budgets(object):

    def __init__(self, accounts):
        self.accounts = accounts

    def _daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + relativedelta(days=n)

    def budget(self, account_name, currency_name, date_from, date_to):
        # find account
        account = None
        for account_ in self.accounts:
            if account_.name == account_name:
                account = account_
                break

        if account == None:
            # print("budget fails account", account_name)
            return None

        # find right currency
        datelines = []
        for dateline in account.datelines:
            if dateline.currency == currency_name:
                datelines.append(dateline)

        if len(datelines) < 1:
            # print("budget fails currency", currency_name)
            return None

        # find lower boundry
        if datelines[0].date_monday > date_from:
            # print("budget fails lower", date_from)
            return None

        budget = 0
        for single_day in self._daterange(date_from, date_to):
            matching_dateline = self._matching_dateline(datelines, single_day)
            budget = budget + (matching_dateline.value / matching_dateline.days)

        return budget

    def _matching_dateline(self, datelines, date_):
        daily_value = 0
        last_seen_dateline = datelines[0].date_monday
        for dateline in datelines:
            if dateline.date_monday <= date_:
                last_seen_dateline = dateline
            else:
                break
        return last_seen_dateline


class Dateline(object):

    def __init__(self, date_monday, period, value, currency):
        super(Dateline, self).__init__()
        self.date_monday = date_monday  # TODO this is not really the date_monday, but the date where the budget-dateline starts
        self.period = period
        self.value = value
        self.currency = currency

        self.days = self._days(self.date_monday, self.period)

    def _days(self, start_date, period):
        # TODO test this extensively, may be buggy
        if period == 'D':
            return 1
        if period == 'W':
            return 7
        if period == 'M':
            return ((start_date + relativedelta(months=1)) - start_date).days
        if period == 'Q':
            return ((start_date + relativedelta(months=3)) - start_date).days
        if period == 'Y':
            return ((start_date + relativedelta(years=1)) - start_date).days
        raise Exception("Period unknown: {}".format(period))

    def __repr__(self):
        return "Dateline ({}, {}, {}, {})".format(self.date_monday, self.period, self.value, self.currency)


class AccountEntry(object):

    def __init__(self, name):
        super(AccountEntry, self).__init__()
        self.name = name
        self.datelines = []

    def __repr__(self):
        return "{}: {}".format(self.name, self.datelines)
