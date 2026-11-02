"""Account name helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beancount.core.account import TYPE as ACCOUNT_TYPE

from fava.beans.abc import Custom
from fava.beans.abc import Pad
from fava.beans.abc import Transaction

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Sequence

    from fava.beans.abc import Directive


def parent(account: str) -> str | None:
    """Get the name of the parent of the given account."""
    parts = account.rsplit(":", maxsplit=1)
    return parts[0] if len(parts) == 2 else None


def root(account: str) -> str:
    """Get root account of the given account."""
    parts = account.split(":", maxsplit=1)
    return parts[0]


def account_tester(
    account: str | tuple[str, ...], *, with_children: bool
) -> Callable[[str], bool]:
    """Get a function to check if an account is equal to the account.

    Arguments:
        account: An account name or tuple of accounts to check.
        with_children: Whether to include all child accounts.
    """
    if isinstance(account, str):
        if with_children:
            account_as_parent = account + ":"

            def is_account(other: str) -> bool:
                return other == account or other.startswith(account_as_parent)

        else:

            def is_account(other: str) -> bool:
                return other == account
    else:
        exact = frozenset(account)
        if with_children:
            accounts_as_parent = tuple(a + ":" for a in account)

            def is_account(other: str) -> bool:
                return other in exact or other.startswith(accounts_as_parent)

        else:

            def is_account(other: str) -> bool:
                return other in exact

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
        return [
            val.value
            for val in entry.values
            if val.dtype == ACCOUNT_TYPE and isinstance(val.value, str)
        ]
    if isinstance(entry, Pad):
        return [entry.account, entry.source_account]
    account_ = getattr(entry, "account", None)
    if account_ is not None:
        return [account_]
    return []
