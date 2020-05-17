"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""
import datetime
import os
import re
import unicodedata
from typing import Any
from typing import MutableMapping
from typing import Optional

import flask
from beancount.core import compare
from beancount.core import realization
from beancount.core.account import ACCOUNT_RE
from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.number import ZERO

from fava.context import g
from fava.core.conversion import cost
from fava.core.conversion import cost_or_value as cost_or_value_without_context
from fava.core.conversion import units
from fava.util.date import Interval


def remove_keys(
    _dict: MutableMapping[str, Any], keys
) -> MutableMapping[str, Any]:
    """Remove keys from a dictionary."""
    if not _dict:
        return {}
    new = dict(_dict)
    for key in keys:
        new.pop(key, None)
    return new


def cost_or_value(inventory, date: Optional[datetime.date] = None) -> Any:
    """Get the cost or value of an inventory."""
    return cost_or_value_without_context(
        inventory, g.conversion, g.ledger.price_map, date
    )


def format_currency(
    value: Decimal, currency: Optional[str] = None, show_if_zero: bool = False
) -> str:
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ""
    if value == ZERO:
        return g.ledger.format_decimal(ZERO, currency)
    return g.ledger.format_decimal(value, currency)


def format_amount(amount: Amount) -> str:
    """Format an amount to string using the DisplayContext."""
    if amount is None:
        return ""
    number, currency = amount
    if number is None:
        return ""
    return f"{format_currency(number, currency, True)} {currency}"


def format_date(date: datetime.date) -> str:
    """Format a date according to the current interval."""
    if g.interval is Interval.YEAR:
        return date.strftime("%Y")
    if g.interval is Interval.QUARTER:
        return f"{date.year}Q{(date.month - 1) // 3 + 1}"
    if g.interval is Interval.MONTH:
        return date.strftime("%b %Y")
    if g.interval is Interval.WEEK:
        return date.strftime("%YW%W")
    if g.interval is Interval.DAY:
        return date.strftime("%Y-%m-%d")
    return ""


def hash_entry(entry) -> str:
    """Hash an entry."""
    return compare.hash_entry(entry)


def balance_children(account):
    """Compute the total balance of an account."""
    return realization.compute_balance(account)


def get_or_create(account, account_name):
    """Get or create a child account."""
    if account.account == account_name:
        return account
    return realization.get_or_create(account, account_name)


FLAGS_TO_TYPES = {"*": "cleared", "!": "pending"}


def flag_to_type(flag):
    """Names for entry flags."""
    return FLAGS_TO_TYPES.get(flag, "other")


def should_show(account) -> bool:
    """Determine whether the account should be shown."""
    if not account.balance_children.is_empty() or any(
        should_show(a) for a in account.children
    ):
        return True
    if account.name not in g.ledger.accounts:
        return False
    if not g.ledger.fava_options[
        "show-closed-accounts"
    ] and g.ledger.account_is_closed(account.name):
        return False
    if (
        not g.ledger.fava_options["show-accounts-with-zero-balance"]
        and account.balance.is_empty()
    ):
        return False
    if (
        not g.ledger.fava_options["show-accounts-with-zero-transactions"]
        and not account.has_txns
    ):
        return False
    return True


def basename(file_path: str) -> str:
    """Return the basename of a filepath."""
    return unicodedata.normalize("NFC", os.path.basename(file_path))


def format_errormsg(message: str) -> str:
    """Match account names in error messages and insert HTML links for them."""
    match = re.search(ACCOUNT_RE, message)
    if not match:
        return message
    account = match.group()
    url = flask.url_for("account", name=account)
    return (
        message.replace(account, f'<a href="{url}">{account}</a>')
        .replace("for '", "for ")
        .replace("': ", ": ")
    )


def collapse_account(account_name: str) -> bool:
    """Return true if account should be collapsed."""
    collapse_patterns = g.ledger.fava_options["collapse-pattern"]
    for pattern in collapse_patterns:
        try:
            if re.match(pattern, account_name):
                return True
        except re.error:
            pass

    return False


FILTERS = [
    balance_children,
    basename,
    collapse_account,
    cost,
    cost_or_value,
    cost_or_value,
    flag_to_type,
    format_amount,
    format_currency,
    format_date,
    format_errormsg,
    get_or_create,
    hash_entry,
    remove_keys,
    should_show,
    units,
]
