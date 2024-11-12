"""Account name helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beancount.core.account import TYPE as ACCOUNT_TYPE

from fava.beans.abc import Custom
from fava.beans.abc import Pad
from fava.beans.abc import Transaction

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence
    from typing import Callable

    from fava.beans.abc import Directive


def parent(account: str) -> str | None:
    """Get the name of the parent of the given account."""
    parts = account.rsplit(":", maxsplit=1)
    return parts[0] if len(parts) == 2 else None


def root(account: str) -> str:
    """Get root account of the given account."""
    parts = account.split(":", maxsplit=1)
    return parts[0]


def child_account_tester(account: str) -> Callable[[str], bool]:
    """Get a function to check if an account is a descendant of the account."""
    account_as_parent = account + ":"

    def is_child_account(other: str) -> bool:
        return other == account or other.startswith(account_as_parent)

    return is_child_account


def account_tester(
    account: str, *, with_children: bool
) -> Callable[[str], bool]:
    """Get a function to check if an account is equal to the account.

    Arguments:
        account: An account name to check.
        with_children: Whether to include all child accounts.
    """
    if with_children:
        return child_account_tester(account)

    def is_account(other: str) -> bool:
        return other == account

    return is_account


def get_entry_accounts(entry: Directive) -> Sequence[str]:
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
