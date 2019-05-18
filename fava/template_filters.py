"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""

import os
import unicodedata
import re

import flask
from flask import g
from beancount.core import compare
from beancount.core import convert
from beancount.core import prices
from beancount.core import realization
from beancount.core.amount import Amount
from beancount.core.number import ZERO
from beancount.core.account import ACCOUNT_RE

from fava.util.date import Interval


def get_market_value(pos, price_map, date=None):
    """Get the market value of a Position.

    This differs from the convert.get_value function in Beancount by returning
    the cost value if no price can be found.

    Args:
        pos: A Position.
        price_map: A dict of prices, as built by prices.build_price_map().
        date: A datetime.date instance to evaluate the value at, or None.

    Returns:
        An Amount, with value converted or if the conversion failed just the
        cost value (or the units if the position has no cost).
    """
    units_ = pos.units
    cost_ = pos.cost
    value_currency = cost_.currency if cost_ else None

    if value_currency:
        base_quote = (units_.currency, value_currency)
        _, price_number = prices.get_price(price_map, base_quote, date)
        if price_number is not None:
            return Amount(units_.number * price_number, value_currency)
        return Amount(units_.number * cost_.number, value_currency)
    return units_


def remove_keys(_dict, keys):
    """Remove keys from a dictionary."""
    if not _dict:
        return {}
    new = dict(_dict)
    for key in keys:
        new.pop(key, None)
    return new


def units(inventory):
    """Get the units of an inventory."""
    return inventory.reduce(convert.get_units)


def cost(inventory):
    """Get the cost of an inventory."""
    return inventory.reduce(convert.get_cost)


def cost_or_value(inventory, date=None):
    """Get the cost or value of an inventory."""
    if g.conversion == "at_value":
        return inventory.reduce(get_market_value, g.ledger.price_map, date)
    if g.conversion == "units":
        return inventory.reduce(convert.get_units)
    if g.conversion:
        return inventory.reduce(
            convert.convert_position, g.conversion, g.ledger.price_map, date
        )
    return inventory.reduce(convert.get_cost)


def format_currency(value, currency=None, show_if_zero=False):
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ""
    if value == ZERO:
        return g.ledger.format_decimal(ZERO, currency)
    return g.ledger.format_decimal(value, currency)


def format_amount(amount):
    """Format an amount to string using the DisplayContext."""
    if amount is None:
        return ""
    number, currency = amount
    if number is None:
        return ""
    return "{} {}".format(format_currency(number, currency, True), currency)


def format_date(date):
    """Format a date according to the current interval."""
    if g.interval is Interval.YEAR:
        return date.strftime("%Y")
    if g.interval is Interval.QUARTER:
        return "{}Q{}".format(date.year, (date.month - 1) // 3 + 1)
    if g.interval is Interval.MONTH:
        return date.strftime("%b %Y")
    if g.interval is Interval.WEEK:
        return date.strftime("%YW%W")
    if g.interval is Interval.DAY:
        return date.strftime("%Y-%m-%d")
    return ""


def hash_entry(entry):
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


def should_show(account):
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


def basename(file_path):
    """Return the basename of a filepath."""
    return unicodedata.normalize("NFC", os.path.basename(file_path))


def format_errormsg(message):
    """Match account names in error messages and insert HTML links for them."""
    match = re.search(ACCOUNT_RE, message)
    if not match:
        return message
    account = match.group()
    url = flask.url_for("account", name=account)
    return (
        message.replace(account, '<a href="{}">{}</a>'.format(url, account))
        .replace("for '", "for ")
        .replace("': ", ": ")
    )


def collapse_account(account_name):
    """Return true if account should be collapsed."""
    collapse_patterns = g.ledger.fava_options["collapse-pattern"]
    for pattern in collapse_patterns:
        try:
            if re.match(pattern, account_name):
                return True
        except re.error:
            pass

    return False
