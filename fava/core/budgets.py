"""Parsing and computing budgets."""

from collections import defaultdict, namedtuple, Counter

from beancount.core.data import Custom
from beancount.core.number import Decimal

from fava.util.date import (
    Interval,
    days_in_daterange,
    number_of_days_in_period,
)
from fava.core.helpers import FavaModule

Budget = namedtuple("Budget", "account date_start period number currency")
BudgetError = namedtuple("BudgetError", "source message entry")


class BudgetModule(FavaModule):
    """Parses budget entries."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.budget_entries = None

    def load_file(self):
        self.budget_entries, errors = parse_budgets(
            self.ledger.all_entries_by_type[Custom]
        )
        self.ledger.errors.extend(errors)

    def calculate(self, account_name, begin_date, end_date):
        """Calculate the budget for an account in an interval."""
        return calculate_budget(
            self.budget_entries, account_name, begin_date, end_date
        )

    def calculate_children(self, account_name, begin_date, end_date):
        """Calculate the budget for an account including its children."""
        return calculate_budget_children(
            self.budget_entries, account_name, begin_date, end_date
        )

    def __bool__(self):
        return bool(self.budget_entries)


def parse_budgets(custom_entries):
    """Parse budget directives from custom entries.

    Args:
        custom_entries: the Custom entries to parse budgets from.

    Returns:
        A dict of accounts to lists of budgets.

    Example:
        2015-04-09 custom "budget" Expenses:Books "monthly" 20.00 EUR
    """

    budgets = defaultdict(list)
    errors = []

    interval_map = {
        "daily": Interval.DAY,
        "weekly": Interval.WEEK,
        "monthly": Interval.MONTH,
        "quarterly": Interval.QUARTER,
        "yearly": Interval.YEAR,
    }

    for entry in custom_entries:
        if entry.type == "budget":
            try:
                interval = interval_map.get(str(entry.values[1].value))
                if not interval:
                    errors.append(
                        BudgetError(
                            entry.meta,
                            "Invalid interval for budget entry",
                            entry,
                        )
                    )
                    continue
                budget = Budget(
                    entry.values[0].value,
                    entry.date,
                    interval,
                    entry.values[2].value.number,
                    entry.values[2].value.currency,
                )
                budgets[budget.account].append(budget)
            except (IndexError, TypeError):
                errors.append(
                    BudgetError(
                        entry.meta, "Failed to parse budget entry", entry
                    )
                )

    return budgets, errors


def _matching_budgets(budgets, account_name, date_active):
    """Find matching budgets.

    Returns:
        The budget that is active on the specified date for the
        specified account.
    """
    last_seen_budgets = {}
    for budget in budgets[account_name]:
        if budget.date_start <= date_active:
            last_seen_budgets[budget.currency] = budget
        else:
            break
    return last_seen_budgets


def calculate_budget(budgets, account_name, date_from, date_to):
    """Calculate budget for an account.

    Args:
        budgets: A list of :class:`Budget` entries.
        account_name: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    if account_name not in budgets:
        return {}

    currency_dict = defaultdict(Decimal)

    for single_day in days_in_daterange(date_from, date_to):
        matches = _matching_budgets(budgets, account_name, single_day)
        for budget in matches.values():
            currency_dict[budget.currency] += (
                budget.number
                / number_of_days_in_period(budget.period, single_day)
            )
    return currency_dict


def calculate_budget_children(budgets, account_name, date_from, date_to):
    """Calculate budget for an account including budgets of its children.

    Args:
        budgets: A list of :class:`Budget` entries.
        account_name: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    currency_dict = Counter()

    for account in budgets.keys():
        if account.startswith(account_name):
            currency_dict.update(
                calculate_budget(budgets, account, date_from, date_to)
            )
    return currency_dict
