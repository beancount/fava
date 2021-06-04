# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime
import enum
from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import Generator
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Type
from typing import Union

from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.core.position import Cost
from beancount.core.position import CostSpec

Account = str
Currency = str
Flag = str
Meta = Dict[str, Any]
Tags = Union[Set[str], FrozenSet[str]]
Links = Tags

EMPTY_SET: Any

class Booking(enum.Enum):
    STRICT: str = ...
    NONE: str = ...
    AVERAGE: str = ...
    FIFO: str = ...
    LIFO: str = ...

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
    currencies: List[Currency]
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
    tolerance: Optional[Decimal]
    diff_amount: Optional[Decimal]

class Posting(NamedTuple):
    account: Account
    units: Union[Amount, Type[MISSING]]
    cost: Optional[Union[Cost, CostSpec]]
    price: Optional[Amount]
    flag: Optional[Flag]
    meta: Optional[Meta]

class Transaction(NamedTuple):
    meta: Meta
    date: datetime.date
    flag: Flag
    payee: Optional[str]
    narration: str
    tags: Tags
    links: Links
    postings: List[Posting]

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
    tags: Optional[Tags]
    links: Optional[Links]

class Custom(NamedTuple):
    meta: Meta
    date: datetime.date
    type: str
    values: List[Any]

# ALL_DIRECTIVES: Any
Directive = Union[
    Open,
    Close,
    Commodity,
    Pad,
    Balance,
    Transaction,
    Note,
    Event,
    Query,
    Price,
    Document,
    Custom,
]
Entries = List[Directive]

def new_metadata(
    filename: Any, lineno: Any, kvlist: Optional[Any] = ...
) -> Meta: ...
def create_simple_posting(
    entry: Transaction, account: str, number: Decimal, currency: str
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
def get_entry(posting_or_entry: Any) -> Optional[Directive]: ...

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
