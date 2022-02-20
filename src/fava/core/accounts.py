"""Account close date and metadata."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import Dict

from beancount.core.account import TYPE as ACCOUNT_TYPE
from beancount.core.data import Custom
from beancount.core.data import Directive
from beancount.core.data import Meta
from beancount.core.data import Pad
from beancount.core.data import Transaction


@dataclass
class AccountData:
    """Holds information about an account."""

    #: The date on which this account is closed (or datetime.date.max).
    close_date: datetime.date = datetime.date.max

    #: The metadata of the Open entry of this account.
    meta: Meta = field(default_factory=dict)


class AccountDict(Dict[str, AccountData]):
    """Account info dictionary."""

    EMPTY = AccountData()

    def __missing__(self, key: str) -> AccountData:
        return self.EMPTY

    def setdefault(
        self, key: str, _: AccountData | None = None
    ) -> AccountData:
        if key not in self:
            self[key] = AccountData()
        return self[key]


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
