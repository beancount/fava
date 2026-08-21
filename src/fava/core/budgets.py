"""Parsing and computing budgets."""

from __future__ import annotations

from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

import msgspec
from beancount.core.amount import Amount

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.util.date import days_in_daterange
from fava.util.date import INTERVALS

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Mapping
    from collections.abc import Sequence

    from fava.beans.abc import Custom
    from fava.core import FavaLedger
    from fava.util.date import Interval


@dataclass(frozen=True, slots=True)
class Budget:
    """A budget entry."""

    account: str
    date_start: datetime.date
    period: Interval
    number: Decimal
    currency: str


BudgetDict = dict[str, list[Budget]]
"""A map of account names to lists of budget entries."""


class BudgetError(BeancountError):
    """Error with a budget."""


class BudgetModule(FavaModule):
    """Parses budget entries."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self._budget_entries: BudgetDict = {}
        self.errors: Sequence[BudgetError] = []

    def load_file(self) -> None:  # noqa: D102
        self._budget_entries, self.errors = parse_budgets(
            self.ledger.all_entries_by_type.Custom
        )

    def calculate(
        self,
        account: str,
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Mapping[str, Decimal]:
        """Calculate the budget for an account in an interval."""
        return calculate_budget(
            self._budget_entries, account, begin_date, end_date
        )

    def calculate_children(
        self,
        account: str,
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Mapping[str, Decimal]:
        """Calculate the budget for an account including its children."""
        return calculate_budget_children(
            self._budget_entries, account, begin_date, end_date
        )


def _parse_budget(entry: Custom) -> Budget:
    values = msgspec.convert(
        tuple(v.value for v in entry.values), tuple[str, str, Amount]
    )
    interval = INTERVALS.get(str(values[1]).lower())
    if not interval:
        msg = "Invalid interval for budget entry"
        raise TypeError(msg)
    return Budget(
        values[0],
        entry.date,
        interval,
        values[2].number or Decimal(),
        values[2].currency,
    )


def parse_budgets(
    custom_entries: Sequence[Custom],
) -> tuple[BudgetDict, Sequence[BudgetError]]:
    """Parse budget directives from custom entries.

    Args:
        custom_entries: the Custom entries to parse budgets from.

    Returns:
        A dict of accounts to lists of budgets.

    Example:
        2015-04-09 custom "budget" Expenses:Books "monthly" 20.00 EUR
    """
    budgets: BudgetDict = defaultdict(list)
    errors = []

    for entry in (entry for entry in custom_entries if entry.type == "budget"):
        try:
            budget = _parse_budget(entry)
            budgets[budget.account].append(budget)
        except (TypeError, msgspec.ValidationError) as error:
            errors.append(
                BudgetError(
                    entry.meta,
                    f"Failed to parse budget entry: {error!s}",
                    entry,
                ),
            )

    return budgets, errors


def _matching_budgets(
    budgets: Sequence[Budget],
    date_active: datetime.date,
) -> Mapping[str, Budget]:
    """Find matching budgets.

    Returns:
        The budget that is active on the specified date for the
        specified account.
    """
    last_seen_budgets = {}
    for budget in budgets:
        if budget.date_start <= date_active:
            last_seen_budgets[budget.currency] = budget
        else:
            break
    return last_seen_budgets


def calculate_budget(
    budgets: BudgetDict,
    account: str,
    date_from: datetime.date,
    date_to: datetime.date,
) -> Mapping[str, Decimal]:
    """Calculate budget for an account.

    Args:
        budgets: A list of :class:`Budget` entries.
        account: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    budget_list = budgets.get(account, None)
    if budget_list is None:
        return {}

    currency_dict: dict[str, Decimal] = defaultdict(Decimal)

    for day in days_in_daterange(date_from, date_to):
        matches = _matching_budgets(budget_list, day)
        for budget in matches.values():
            days_in_period = budget.period.number_of_days(day)
            currency_dict[budget.currency] += budget.number / days_in_period
    return dict(currency_dict)


def calculate_budget_children(
    budgets: BudgetDict,
    account: str,
    date_from: datetime.date,
    date_to: datetime.date,
) -> Mapping[str, Decimal]:
    """Calculate budget for an account including budgets of its children.

    Args:
        budgets: A list of :class:`Budget` entries.
        account: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    currency_dict: dict[str, Decimal] = Counter()  # type: ignore[assignment]  # ty:ignore[invalid-assignment]

    for child in budgets:
        if child.startswith(account):
            currency_dict.update(
                calculate_budget(budgets, child, date_from, date_to),
            )
    return dict(currency_dict)
