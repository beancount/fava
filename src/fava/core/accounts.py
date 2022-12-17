"""Account close date and metadata."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import Dict

from beancount.core.account import TYPE as ACCOUNT_TYPE
from beancount.core.compare import hash_entry
from beancount.core.data import Balance
from beancount.core.data import Close
from beancount.core.data import Custom
from beancount.core.data import Directive
from beancount.core.data import get_entry
from beancount.core.data import Meta
from beancount.core.data import Pad
from beancount.core.data import Transaction
from beancount.core.data import TxnPosting
from beancount.core.realization import find_last_active_posting
from beancount.core.realization import get
from beancount.core.realization import RealAccount

from fava.core._compat import FLAG_UNREALIZED
from fava.core.conversion import units
from fava.core.module_base import FavaModule


def uptodate_status(real_account: RealAccount) -> str | None:
    """Status of the last balance or transaction.

    Args:
        account_name: An account name.

    Returns:
        A status string for the last balance or transaction of the account.

        - 'green':  A balance check that passed.
        - 'red':    A balance check that failed.
        - 'yellow': Not a balance check.
    """
    for txn_posting in reversed(real_account.txn_postings):
        if isinstance(txn_posting, Balance):
            if txn_posting.diff_amount:
                return "red"
            return "green"
        if (
            isinstance(txn_posting, TxnPosting)
            and txn_posting.txn.flag != FLAG_UNREALIZED
        ):
            return "yellow"
    return None


def balance_string(real_account: RealAccount) -> str:
    """Balance directive for the given account for today."""
    account = real_account.account
    today = str(datetime.date.today())
    res = ""
    for pos in units(real_account.balance):
        res += (
            f"{today} balance {account:<28}"
            + f" {pos.units.number:>15} {pos.units.currency}\n"
        )
    return res


@dataclass
class LastEntry:
    """Date and hash of the last entry for an account."""

    #: The entry date.
    date: datetime.date

    #: The entry hash.
    entry_hash: str


@dataclass
class AccountData:
    """Holds information about an account."""

    #: The date on which this account is closed (or datetime.date.max).
    close_date: datetime.date = datetime.date.max

    #: The metadata of the Open entry of this account.
    meta: Meta = field(default_factory=dict)

    #: Uptodate status. Is only computed if the account has a
    #: "fava-uptodate-indication" meta attribute.
    uptodate_status: str | None = None

    #: Balance directive if this account has an uptodate status.
    balance_string: str | None = None

    #: The last entry of the account (unless it is a close Entry)
    last_entry: LastEntry | None = None


class AccountDict(FavaModule, Dict[str, AccountData]):
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

    def load_file(self) -> None:
        self.clear()
        all_root_account = self.ledger.all_root_account
        for open_entry in self.ledger.all_entries_by_type.Open:
            meta = open_entry.meta
            account_data = self.setdefault(open_entry.account)
            account_data.meta = meta

            real_account = get(all_root_account, open_entry.account)
            assert real_account is not None
            last = find_last_active_posting(real_account.txn_postings)
            if last is not None and not isinstance(last, Close):
                entry = get_entry(last)
                account_data.last_entry = LastEntry(
                    date=entry.date, entry_hash=hash_entry(entry)
                )
            if meta.get("fava-uptodate-indication"):
                account_data.uptodate_status = uptodate_status(real_account)
                if account_data.uptodate_status != "green":
                    account_data.balance_string = balance_string(real_account)
        for close in self.ledger.all_entries_by_type.Close:
            self.setdefault(close.account).close_date = close.date

    def all_balance_directives(self) -> str:
        """Balance directives for all accounts."""
        return "".join(
            account_details.balance_string
            for account_details in self.values()
            if account_details.balance_string
        )


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
