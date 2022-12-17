# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime
import enum
from collections.abc import Generator
from typing import Any
from typing import NamedTuple
from typing import TypeAlias

from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.core.position import Cost
from beancount.core.position import CostSpec

Account = str
Currency = str
Flag = str
Meta: TypeAlias = dict[str, Any]
Tags: TypeAlias = set[str] | frozenset[str]
Links = Tags

EMPTY_SET: Any

class Booking(enum.Enum):
    STRICT: str
    NONE: str
    AVERAGE: str
    FIFO: str
    LIFO: str

class Close(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account

class Commodity(NamedTuple):
    meta: Meta
    date: datetime.date
    currency: Currency

class Open(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account
    currencies: list[Currency]
    booking: Booking

class Pad(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account
    source_account: Account

class Balance(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account
    amount: Amount
    tolerance: Decimal | None
    diff_amount: Amount | None

class Posting(NamedTuple):
    account: Account
    units: Amount | type[MISSING]
    cost: Cost | CostSpec | None
    price: Amount | None
    flag: Flag | None
    meta: Meta | None

class Transaction(NamedTuple):
    meta: Meta
    date: datetime.date
    flag: Flag
    payee: str | None
    narration: str
    tags: Tags
    links: Links
    postings: list[Posting]

class TxnPosting(NamedTuple):
    txn: Transaction
    posting: Posting

class Note(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account
    comment: str

class Event(NamedTuple):
    meta: Meta
    date: datetime.date
    type: str
    description: str

class Query(NamedTuple):
    meta: Meta
    date: datetime.date
    name: str
    query_string: str

class Price(NamedTuple):
    meta: Meta
    date: datetime.date
    currency: Currency
    amount: Amount

class Document(NamedTuple):
    meta: Meta
    date: datetime.date
    account: Account
    filename: str
    tags: Tags | None
    links: Links | None

class Custom(NamedTuple):
    meta: Meta
    date: datetime.date
    type: str
    values: list[Any]

# ALL_DIRECTIVES: Any
Directive: TypeAlias = (
    Open
    | Close
    | Commodity
    | Pad
    | Balance
    | Transaction
    | Note
    | Event
    | Query
    | Price
    | Document
    | Custom
)

Entries: TypeAlias = list[Directive]

def new_metadata(
    filename: Any, lineno: Any, kvlist: Any | None = ...
) -> Meta: ...
def create_simple_posting(
    entry: Transaction,
    account: str,
    number: Decimal | None,
    currency: str | None,
) -> None: ...

# def create_simple_posting_with_cost(
#     entry: Any,
#     account: Any,
#     number: Any,
#     currency: Any,
#     cost_number: Any,
#     cost_currency: Any,
# ): ...

NoneType: Any

# def sanity_check_types(
#     entry: Any, allow_none_for_tags_and_links: bool = ...
# ) -> None: ...
# def posting_has_conversion(posting: Any): ...
# def transaction_has_conversion(transaction: Any): ...
def get_entry(posting_or_entry: Directive | TxnPosting) -> Directive: ...

SORT_ORDER: Any

# def entry_sortkey(entry: Any): ...
# pylint: disable=redefined-builtin
def sorted(entries: Entries) -> Entries: ...

# def posting_sortkey(entry: Any): ...
# def filter_txns(entries: Any) -> None: ...
# def has_entry_account_component(entry: Any, component: Any): ...
# def find_closest(entries: Any, filename: Any, lineno: Any): ...
# def remove_account_postings(account: Any, entries: Any): ...
def iter_entry_dates(
    entries: Entries, date_begin: datetime.date, date_end: datetime.date
) -> Generator[Directive, None, None]: ...
