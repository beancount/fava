import datetime
import enum
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from decimal import Decimal
from typing import Any
from typing import NamedTuple
from typing import TypeAlias

from beancount.core.amount import Amount
from beancount.core.number import MISSING
from beancount.core.position import Cost
from beancount.core.position import CostSpec

from fava.beans import abc

Account: TypeAlias = str
Currency: TypeAlias = str
Flag: TypeAlias = str
Meta: TypeAlias = Mapping[str, Any]
Tags: TypeAlias = set[str] | frozenset[str]
Links: TypeAlias = Tags

EMPTY_SET: frozenset[str]

class Booking(enum.Enum):
    STRICT = "STRICT"
    NONE = "NONE"
    AVERAGE = "AVERAGE"
    FIFO = "FIFO"
    LIFO = "LIFO"

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
    booking: Booking | None

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
    tags: Tags | None
    links: Links | None

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

def iter_entry_dates(
    entries: Sequence[abc.Directive],
    date_begin: datetime.date,
    date_end: datetime.date,
) -> Iterable[abc.Directive]: ...
