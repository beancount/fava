# pylint: disable=all
# flake8: noqa
from typing import Any
from typing import Optional

from beancount.core import prices as prices
from beancount.core.amount import Amount as Amount
from beancount.core.number import Decimal as Decimal
from beancount.core.number import MISSING as MISSING
from beancount.core.position import Cost as Cost
from beancount.core.position import Position as Position

def get_units(pos: Any): ...
def get_cost(pos: Any): ...
def get_weight(pos: Any): ...
def get_value(pos: Any, price_map: Any, date: Optional[Any] = ...): ...
def convert_position(
    pos: Any, target_currency: Any, price_map: Any, date: Optional[Any] = ...
): ...
def convert_amount(
    amt: Any,
    target_currency: Any,
    price_map: Any,
    date: Optional[Any] = ...,
    via: Optional[Any] = ...,
): ...
