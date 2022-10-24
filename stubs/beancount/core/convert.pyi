# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime

from beancount.core.amount import Amount
from beancount.core.position import Position
from beancount.core.prices import PriceMap

def get_units(pos: Position) -> Amount: ...
def get_cost(pos: Position) -> Amount: ...
def get_weight(pos: Position) -> Amount: ...
def get_value(
    pos: Position, price_map: PriceMap, date: datetime.date | None = ...
) -> Amount: ...
def convert_position(
    pos: Position,
    target_currency: str,
    price_map: PriceMap,
    date: datetime.date | None = ...,
) -> Amount: ...
def convert_amount(
    amt: Amount,
    target_currency: str,
    price_map: PriceMap,
    date: datetime.date | None = ...,
    via: str | None = ...,
) -> Amount: ...
