from dateutil.relativedelta import relativedelta

from beancount.core.data import Custom


class Budgets(object):
    def __init__(self, entries):
        accounts = {}
        for entry in entries:
            if isinstance(entry, Custom):
                if entry.type == 'budget':
                    account_name = entry.values[0].value

                    if account_name not in accounts:
                        accounts[account_name] = \
                            AccountEntry(name=account_name)

                    accounts[account_name].datelines.append(
                        Dateline(date_monday=entry.date,
                                 period=entry.values[1].value,
                                 value=entry.values[2].value.number,
                                 currency=entry.values[2].value.currency)
                    )

        for name, account in accounts.items():
            accounts[name].datelines = sorted(accounts[name].datelines,
                                              key=lambda
                                              dateline: dateline.date_monday)

        self.accounts = accounts.values()

    def _daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + relativedelta(days=n)

    def budget(self, account_name, currency_name, date_from, date_to):
        # find account
        account = None
        for account_ in self.accounts:
            if account_.name == account_name:
                account = account_
                break

        if account is None:
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
            budget = budget + \
                (matching_dateline.value / matching_dateline.days)

        return budget

    def _matching_dateline(self, datelines, date_):
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
        self.date_monday = date_monday
        # TODO this is not really the date_monday, but the date where the
        #      budget-dateline starts
        self.period = period
        self.value = value
        self.currency = currency

        self.days = self._days(self.date_monday, self.period)

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
            .format(self.date_monday, self.period, self.value, self.currency)


class AccountEntry(object):

    def __init__(self, name):
        super(AccountEntry, self).__init__()
        self.name = name
        self.datelines = []

    def __repr__(self):
        return "{}: {}".format(self.name, self.datelines)
