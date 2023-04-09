from collections.abc import Iterable
from collections.abc import Iterator

from beancount.core.data import Directive
from beancount.core.data import TxnPosting
from beancount.core.inventory import Inventory

from fava.beans import abc

class RealAccount(dict[str, RealAccount]):
    account: str
    txn_postings: list[abc.Directive | abc.TxnPosting]
    balance: Inventory

def iter_children(
    real_account: RealAccount, leaf_only: bool = ...
) -> Iterator[RealAccount]: ...
def get(
    real_account: RealAccount,
    account_name: str,
    default: RealAccount | None = ...,
) -> RealAccount: ...
def get_or_create(
    real_account: RealAccount, account_name: str
) -> RealAccount: ...
def realize(
    entries: list[Directive],
    min_accounts: Iterable[str] | None = ...,
    compute_balance: bool = ...,
) -> RealAccount: ...
def get_postings(
    real_account: RealAccount,
) -> list[abc.Directive | abc.TxnPosting]: ...
def iterate_with_balance(
    txn_postings: list[Directive | TxnPosting],
) -> list[tuple[abc.Directive, list[abc.Posting], Inventory, Inventory]]: ...
def compute_balance(real_account: RealAccount) -> Inventory: ...
def find_last_active_posting(
    txn_postings: list[Directive | TxnPosting],
) -> Directive: ...
