from collections import defaultdict, namedtuple

from beancount.core.data import Custom
from beancount.core.number import Decimal

from fava.util.date import days_in_daterange, number_of_days_in_period

Budget = namedtuple('Budget', 'account date_start period number currency')
BudgetError = namedtuple('BudgetError', 'source message entry')


def _parse_budget_entry(entry):
    return Budget(
        entry.values[0].value,
        entry.date,
        entry.values[1].value,
        entry.values[2].value.number,
        entry.values[2].value.currency)


class Budgets(object):

    def __init__(self, entries):
        """
        Reads budget directives from the specified list of beancount entries.

        Example for a budget directive:

        2015-04-09 custom "budget" Expenses:Books "monthly"  20.00 EUR
        """
        self.budgets = defaultdict(lambda: [])
        self.errors = []

        for entry in entries:
            if isinstance(entry, Custom) and entry.type == 'budget':
                try:
                    budget = _parse_budget_entry(entry)
                    self.budgets[budget.account].append(budget)
                except:
                    self.errors.append(BudgetError(
                        entry.meta,
                        'Failed to parse budget entry',
                        entry))

        for name in self.budgets.keys():
            self.budgets[name] = sorted(self.budgets[name],
                                        key=lambda budget: budget.date_start)

    def __bool__(self):
        return bool(self.budgets)

    def _matching_budget(self, account_name, date_active):
        """
        Returns the budget that is active on the specifed date for the
        specified account.
        """
        last_seen_budget = None
        for budget in self.budgets[account_name]:
            if budget.date_start <= date_active:
                last_seen_budget = budget
            else:
                break
        return last_seen_budget

    def budget(self, account_name, date_from, date_to):
        """
        Returns a dictionary (currency => number) with the budget for the
        specified account and period (excluding date_to).
        """
        currency_dict = defaultdict(lambda: Decimal(0.0))

        if account_name not in self.budgets.keys():
            return currency_dict

        for single_day in days_in_daterange(date_from, date_to):
            budget = self._matching_budget(account_name, single_day)
            if budget:
                currency_dict[budget.currency] += \
                    budget.number / number_of_days_in_period(budget.period,
                                                             single_day)
        return dict(currency_dict)
