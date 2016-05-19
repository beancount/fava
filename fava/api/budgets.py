from collections import defaultdict, namedtuple

from beancount.core.data import Custom
from beancount.core.number import Decimal

from fava.util.date import days_in_daterange, number_of_days_in_period


class Budgets(object):
    Budget = namedtuple('Budget', 'date_start period number currency')

    def __init__(self, entries):
        """
        Reads budget directives from the specified list of beancount entries.

        Example for a budget directive:

            2015-04-09 custom "budget" Expenses:Books "monthly"  20.00 EUR
        """
        self.budgets = defaultdict(lambda: [])
        self.currencies = set()

        for entry in entries:
            if isinstance(entry, Custom) and entry.type == 'budget':
                account_name = entry.values[0].value

                self.budgets[account_name].append(
                    Budgets.Budget(date_start=entry.date,
                                   period=entry.values[1].value,
                                   number=entry.values[2].value.number,
                                   currency=entry.values[2].value.currency)
                )

                self.currencies.add(entry.values[2].value.currency)

        for name, account in self.budgets.items():
            self.budgets[name] = sorted(self.budgets[name],
                                        key=lambda
                                        budget: budget.date_start)

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

    def has_budgets(self):
        return len(self.budgets) > 0
