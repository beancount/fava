"""Account name helpers."""
from __future__ import annotations

from beancount.core.account import TYPE as ACCOUNT_TYPE

from fava.beans.abc import Custom
from fava.beans.abc import Directive
from fava.beans.abc import Pad
from fava.beans.abc import Transaction


def parent(acc: str) -> str | None:
    """Get the name of the parent of the given account."""
    parts = acc.rsplit(":", maxsplit=1)
    return parts[0] if len(parts) == 2 else None


def root(acc: str) -> str:
    """Get root account of the given account."""
    parts = acc.split(":", maxsplit=1)
    return parts[0]


def get_entry_accounts(entry: Directive) -> list[str]:
    """Accounts for an entry.

    Args:
        entry: An entry.

    Returns:
        A list with the entry's accounts ordered by priority: For
        transactions the posting accounts are listed in reverse order.
    """
    if isinstance(entry, Transaction):
        return list(reversed([p.account for p in entry.postings]))
    if isinstance(entry, Custom):
        return [val.value for val in entry.values if val.dtype == ACCOUNT_TYPE]
    if isinstance(entry, Pad):
        return [entry.account, entry.source_account]
    account_ = getattr(entry, "account", None)
    if account_ is not None:
        return [account_]
    return []
