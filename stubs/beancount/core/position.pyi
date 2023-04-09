import datetime
from decimal import Decimal
from typing import NamedTuple

from beancount.core.amount import Amount

class Cost(NamedTuple):
    number: Decimal
    currency: str
    date: datetime.date
    label: str | None

class CostSpec(NamedTuple):
    number_per: Decimal | None
    number_total: Decimal | None
    currency: str | None
    date: datetime.date | None
    label: str | None
    merge: bool | None

class Position(NamedTuple):
    units: Amount
    cost: Cost
