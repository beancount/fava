"""Account close date and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import TYPE_CHECKING

from fava.beans.abc import Balance
from fava.beans.abc import Close
from fava.beans.flags import FLAG_UNREALIZED
from fava.beans.funcs import hash_entry
from fava.core.conversion import units
from fava.core.group_entries import group_entries_by_account
from fava.core.group_entries import TransactionPosting
from fava.core.module_base import FavaModule
from fava.core.tree import Tree
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Directive
    from fava.beans.abc import Meta
    from fava.core.tree import TreeNode


def get_last_entry(
    txn_postings: list[Directive | TransactionPosting],
) -> Directive | None:
    """Last entry."""
    for txn_posting in reversed(txn_postings):
        if (
            isinstance(txn_posting, TransactionPosting)
            and txn_posting.transaction.flag == FLAG_UNREALIZED
        ):
            continue

        if isinstance(txn_posting, TransactionPosting):
            return txn_posting.transaction
        return txn_posting
    return None


def uptodate_status(
    txn_postings: list[Directive | TransactionPosting],
) -> str | None:
    """Status of the last balance or transaction.

    Args:
        txn_postings: The TransactionPosting for the account.

    Returns:
        A status string for the last balance or transaction of the account.

        - 'green':  A balance check that passed.
        - 'red':    A balance check that failed.
        - 'yellow': Not a balance check.
    """
    for txn_posting in reversed(txn_postings):
        if isinstance(txn_posting, Balance):
            if txn_posting.diff_amount:
                return "red"
            return "green"
        if (
            isinstance(txn_posting, TransactionPosting)
            and txn_posting.transaction.flag != FLAG_UNREALIZED
        ):
            return "yellow"
    return None


def balance_string(tree_node: TreeNode) -> str:
    """Balance directive for the given account for today."""
    account = tree_node.name
    today = str(local_today())
    res = ""
    for currency, number in units(tree_node.balance).items():
        res += f"{today} balance {account:<28} {number:>15} {currency}\n"
    return res


@dataclass(frozen=True)
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
    close_date: datetime.date | None = None

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
        self,
        key: str,
        _: AccountData | None = None,
    ) -> AccountData:
        """Get the account of the given name, insert one if it is missing."""
        if key not in self:
            self[key] = AccountData()
        return self[key]

    def load_file(self) -> None:  # noqa: D102
        self.clear()
        entries_by_account = group_entries_by_account(self.ledger.all_entries)
        tree = Tree(self.ledger.all_entries)
        for open_entry in self.ledger.all_entries_by_type.Open:
            meta = open_entry.meta
            account_data = self.setdefault(open_entry.account)
            account_data.meta = meta

            txn_postings = entries_by_account[open_entry.account]
            last = get_last_entry(txn_postings)
            if last is not None and not isinstance(last, Close):
                account_data.last_entry = LastEntry(
                    date=last.date,
                    entry_hash=hash_entry(last),
                )
            if meta.get("fava-uptodate-indication"):
                account_data.uptodate_status = uptodate_status(txn_postings)
                if account_data.uptodate_status != "green":
                    account_data.balance_string = balance_string(
                        tree.get(open_entry.account),
                    )
        for close in self.ledger.all_entries_by_type.Close:
            self.setdefault(close.account).close_date = close.date

    def all_balance_directives(self) -> str:
        """Balance directives for all accounts."""
        return "".join(
            account_details.balance_string
            for account_details in self.values()
            if account_details.balance_string
        )
