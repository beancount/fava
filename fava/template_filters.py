"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""

import os
import unicodedata

from flask import g
from beancount.core import compare
from beancount.core import convert
from beancount.core import data
from beancount.core import prices
from beancount.core import realization
from beancount.core.amount import Amount
from beancount.core.number import Decimal


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
        return None
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
    if g.conversion == 'at_value':
        return inventory.reduce(get_market_value, g.ledger.price_map, date)
    if g.conversion:
        return inventory.reduce(convert.convert_position, g.conversion,
                                g.ledger.price_map, date)
    return inventory.reduce(convert.get_cost)


def format_currency(value, currency=None, show_if_zero=False):
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ''
    if value == 0.0:
        return g.ledger.quantize(Decimal(0.0), currency)
    return g.ledger.quantize(value, currency)


def format_amount(amount):
    """Format an amount to string using the DisplayContext."""
    if not amount:
        return ''
    number, currency = amount
    if not number:
        return ''
    return "{} {}".format(format_currency(number, currency), currency)


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


FLAGS_TO_TYPES = {'*': 'cleared', '!': 'pending'}


def flag_to_type(flag):
    """Names for entry flags."""
    return FLAGS_TO_TYPES.get(flag, 'other')


def show_journal_entry(entry):
    """Determine whether the entry is shown in the journal."""
    if isinstance(entry, data.Transaction):
        if flag_to_type(entry.flag) not in g.journal_show:
            return False
    if isinstance(entry, data.Document):
        if 'statement' in entry.tags and 'statement' not in g.journal_show:
            return False
        if 'discovered' in entry.tags and 'discovered' not in g.journal_show:
            return False
    entry_type = entry.__class__.__name__.lower()
    if entry_type not in g.journal_show:
        return False
    return True


def should_show(account):
    """Determine whether the account should be shown."""
    if (not account.balance_children.is_empty()
            or any(should_show(a) for a in account.children)):
        return True
    if account.name not in g.ledger.accounts:
        return False
    if (not g.ledger.fava_options['show-closed-accounts']
            and g.ledger.account_is_closed(account.name)):
        return False
    if (not g.ledger.fava_options['show-accounts-with-zero-balance']
            and account.balance.is_empty()):
        return False
    if (not g.ledger.fava_options['show-accounts-with-zero-transactions']
            and not account.has_txns):
        return False
    return True


def basename(file_path):
    """Return the basename of a filepath."""
    return unicodedata.normalize('NFC', os.path.basename(file_path))
