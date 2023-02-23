"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""
from __future__ import annotations

import datetime
from os.path import basename as path_basename
from typing import Any
from typing import MutableMapping
from typing import TypeVar
from unicodedata import normalize

from beancount.core import compare
from beancount.core import realization
from beancount.core.data import Directive
from beancount.core.inventory import Inventory
from beancount.core.number import Decimal
from beancount.core.number import ZERO

from fava.context import g
from fava.core.conversion import cost
from fava.core.conversion import units
from fava.core.conversion import cost_or_value as cost_or_value_without_context
from fava.core.tree import TreeNode

MappingValue = TypeVar("MappingValue")


def remove_keys(
    _dict: MutableMapping[str, MappingValue] | None, keys: list[str]
) -> MutableMapping[str, MappingValue]:
    """Remove keys from a dictionary."""
    if not _dict:
        return {}
    new = dict(_dict)
    for key in keys:
        try:
            del new[key]
        except KeyError:
            pass
    return new


def cost_or_value(
    inventory: Inventory, date: datetime.date | None = None
) -> Any:
    """Get the cost or value of an inventory."""
    return cost_or_value_without_context(
        inventory, g.conversion, g.ledger.price_map, date
    )


def format_currency(
    value: Decimal,
    currency: str | None = None,
    show_if_zero: bool = False,
    invert: bool = False,
) -> str:
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ""
    if value == ZERO:
        return g.ledger.format_decimal(ZERO, currency)
    if invert:
        value = -value
    return g.ledger.format_decimal(value, currency)


def format_date(date: datetime.date) -> str:
    """Format a date according to the current interval."""
    return g.interval.format_date(date)


def format_date_filter(date: datetime.date) -> str:
    """Format a date according to the current interval for the time filter."""
    return g.interval.format_date_filter(date)


def hash_entry(entry: Directive) -> str:
    """Hash an entry."""
    return compare.hash_entry(entry)


def balance_children(account: realization.RealAccount) -> Inventory:
    """Compute the total balance of an account."""
    return realization.compute_balance(account)


def get_or_create(
    account: realization.RealAccount, account_name: str
) -> realization.RealAccount:
    """Get or create a child account."""
    if account.account == account_name:
        return account
    return realization.get_or_create(account, account_name)


FLAGS_TO_TYPES = {"*": "cleared", "!": "pending"}


def flag_to_type(flag: str) -> str:
    """Names for entry flags."""
    return FLAGS_TO_TYPES.get(flag, "other")


def should_show(account: TreeNode) -> bool:
    """Determine whether the account should be shown."""
    if not account.balance_children.is_empty() or any(
        should_show(a) for a in account.children
    ):
        return True
    ledger = g.ledger
    filtered = g.filtered
    if account.name not in ledger.accounts:
        return False
    fava_options = ledger.fava_options
    if not fava_options.show_closed_accounts and filtered.account_is_closed(
        account.name
    ):
        return False
    if (
        not fava_options.show_accounts_with_zero_balance
        and account.balance.is_empty()
    ):
        return False
    if (
        not fava_options.show_accounts_with_zero_transactions
        and not account.has_txns
    ):
        return False
    return True


def basename(file_path: str) -> str:
    """Return the basename of a filepath."""
    return normalize("NFC", path_basename(file_path))


def collapse_account(account_name: str) -> bool:
    """Return true if account should be collapsed."""
    collapse_patterns = g.ledger.fava_options.collapse_pattern
    return any(pattern.match(account_name) for pattern in collapse_patterns)


FILTERS = [
    balance_children,
    basename,
    collapse_account,
    cost,
    cost_or_value,
    cost_or_value,
    flag_to_type,
    format_currency,
    format_date,
    format_date_filter,
    get_or_create,
    hash_entry,
    remove_keys,
    should_show,
    units,
]
