"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""

import os

from flask import g
from beancount.core import realization
from beancount.core.data import Close, TxnPosting
from beancount.core.number import Decimal


def remove_keys(_dict, keys):
    """Remove keys from a dictionary."""
    if not _dict:
        return None
    new = dict(_dict)
    for key in keys:
        new.pop(key, None)
    return new


def format_currency(value, currency=None, show_if_zero=False):
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ''
    if value == 0.0:
        return g.api.quantize(Decimal(0.0), currency)
    return g.api.quantize(value, currency)


def format_amount(amount):
    """Format an amount to string using the DisplayContext."""
    if not amount:
        return ''
    return "{} {}".format(format_currency(amount.number, amount.currency),
                          amount.currency)


def last_segment(account_name):
    """Get the last segment of an account."""
    return account_name.split(':')[-1]


def account_level(account_name):
    """Get the depth of an account."""
    return account_name.count(":")+1


def balance_children(account):
    """Compute the total balance of an account."""
    return realization.compute_balance(account)


def get_or_create(account, account_name):
    """Get or create a child account."""
    if account.account == account_name:
        return account
    return realization.get_or_create(account, account_name)


def should_show(account):
    """Determine whether the account should be shown."""
    show_this_account = False
    # check if it's a leaf account
    if len(account) == 0 or bool(account.txn_postings):
        show_this_account = True
        if not g.api.fava_options['show-closed-accounts'] and \
                isinstance(realization.find_last_active_posting(
                        account.txn_postings), Close):
            show_this_account = False
        if not g.api.fava_options['show-accounts-with-zero-balance'] and \
                account.balance.is_empty():
            show_this_account = False
        if not g.api.fava_options['show-accounts-with-zero-transactions'] and \
                not any(isinstance(t, TxnPosting)
                        for t in account.txn_postings):
            show_this_account = False
    return show_this_account or any(
        should_show(a) for a in account.values())


def basename(file_path):
    """Return the basename of a filepath."""
    return os.path.basename(file_path)


def should_collapse_account(account_name):
    """Determine whether the children of an account should be hidden."""
    key = 'fava-collapse-account'
    if key in g.api.account_metadata(account_name):
        return g.api.account_metadata(account_name)[key] == 'True'
    else:
        return False


def uptodate_eligible(account_name):
    """Determine whether uptodate-indicators should be shown for an account."""
    key = 'fava-uptodate-indication'
    if key in g.api.account_metadata(account_name):
        return g.api.account_metadata(account_name)[key] == 'True'
    else:
        return False
