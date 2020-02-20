# pylint: disable=all
# flake8: noqa
import datetime
import enum
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from beancount.core.account import has_component as has_component
from beancount.core.amount import Amount as Amount
from beancount.core.number import D as D
from beancount.core.number import Decimal as Decimal
from beancount.core.position import Cost as Cost
from beancount.core.position import CostSpec as CostSpec
from beancount.utils.bisect_key import (
    bisect_left_with_key as bisect_left_with_key,
)

Account = str
Currency = str
Flag = str
Meta = Dict[str, Any]
EMPTY_SET: Any

class Booking(enum.Enum):
    STRICT: str = ...
    NONE: str = ...
    AVERAGE: str = ...
    FIFO: str = ...
    LIFO: str = ...

class DirectiveBase(NamedTuple):
    meta: Meta
    date: datetime.date

class Close(DirectiveBase):
    account: Account

class Commodity(DirectiveBase):
    currency: Currency

class Open(DirectiveBase):
    account: Account
    currencies: List[Currency]
    booking: Booking

class Pad(DirectiveBase):
    account: Account
    source_account: Account

class Balance(DirectiveBase):
    account: Account
    amount: Amount
    tolerance: Optional[Decimal]
    diff_amount: Optional[Decimal]

class Posting(NamedTuple):
    account: Account
    units: Amount
    cost: Optional[Union[Cost, CostSpec]]
    price: Optional[Amount]
    flag: Optional[Flag]
    meta: Optional[Meta]

class Transaction(DirectiveBase):
    flag: Flag
    payee: Optional[str]
    narration: str
    tags: Set
    links: Set
    postings: List[Posting]

class TxnPosting(NamedTuple):
    txn: Transaction
    posting: Posting

class Note(DirectiveBase):
    account: Account
    comment: str

class Event(DirectiveBase):
    type: str
    description: str

class Query(DirectiveBase):
    name: str
    query_string: str

class Price(DirectiveBase):
    currency: Currency
    amount: Amount

class Document(DirectiveBase):
    account: Account
    filename: str
    tags: Optional[Set]
    links: Optional[Set]

class Custom(DirectiveBase):
    type: str
    values: List

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

def new_metadata(filename: Any, lineno: Any, kvlist: Optional[Any] = ...): ...
def create_simple_posting(
    entry: Any, account: Any, number: Any, currency: Any
): ...
def create_simple_posting_with_cost(
    entry: Any,
    account: Any,
    number: Any,
    currency: Any,
    cost_number: Any,
    cost_currency: Any,
): ...

NoneType: Any

def sanity_check_types(
    entry: Any, allow_none_for_tags_and_links: bool = ...
) -> None: ...
def posting_has_conversion(posting: Any): ...
def transaction_has_conversion(transaction: Any): ...
def get_entry(posting_or_entry: Any): ...

SORT_ORDER: Any

def entry_sortkey(entry: Any): ...
def sorted(entries: Any): ...
def posting_sortkey(entry: Any): ...
def filter_txns(entries: Any) -> None: ...
def has_entry_account_component(entry: Any, component: Any): ...
def find_closest(entries: Any, filename: Any, lineno: Any): ...
def remove_account_postings(account: Any, entries: Any): ...
def iter_entry_dates(entries: Any, date_begin: Any, date_end: Any): ...
