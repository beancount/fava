"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""

import os

from flask import g
from beancount.core import convert, compare, realization
from beancount.core import data
from beancount.core.number import Decimal


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
        return inventory.reduce(convert.get_value, g.ledger.price_map, date)
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
    return "{} {}".format(
        format_currency(amount.number, amount.currency), amount.currency)


def hash_entry(entry):
    """Hash an entry."""
    return compare.hash_entry(entry)


def last_segment(account_name):
    """Get the last segment of an account."""
    return account_name.split(':')[-1]


def account_level(account_name):
    """Get the depth of an account."""
    return account_name.count(":") + 1


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
    show_this_account = False
    # check if it's a leaf account
    if not account or account.txn_postings:
        show_this_account = True
        if (not g.ledger.fava_options['show-closed-accounts'] and isinstance(
                realization.find_last_active_posting(account.txn_postings),
                data.Close)):
            show_this_account = False
        if (not g.ledger.fava_options['show-accounts-with-zero-balance'] and
                account.balance.is_empty()):
            show_this_account = False
        if (not g.ledger.fava_options['show-accounts-with-zero-transactions']
                and not any(
                    isinstance(t, data.TxnPosting)
                    for t in account.txn_postings)):
            show_this_account = False
    return show_this_account or any(should_show(a) for a in account.values())


def basename(file_path):
    """Return the basename of a filepath."""
    return os.path.basename(file_path)


def should_collapse_account(account_name):
    """Determine whether the children of an account should be hidden."""
    return g.ledger.account_metadata(account_name).get(
        'fava-collapse-account') == 'True'


def uptodate_eligible(account_name):
    """Determine whether uptodate-indicators should be shown for an account."""
    return g.ledger.account_metadata(account_name).get(
        'fava-uptodate-indication') == 'True'
