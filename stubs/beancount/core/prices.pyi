# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime
from decimal import Decimal
from typing import TypeAlias

from beancount.core.data import Directive

BaseQuote: TypeAlias = tuple[str, str]
_DateAndPrice: TypeAlias = tuple[datetime.date, Decimal]

class PriceMap(dict[tuple[str, str], list[_DateAndPrice]]):
    forward_pairs: list[BaseQuote]

def build_price_map(entries: list[Directive]) -> PriceMap: ...
def get_all_prices(
    price_map: PriceMap, base_quote: BaseQuote
) -> list[_DateAndPrice]: ...
def get_price(
    price_map: PriceMap,
    base_quote: BaseQuote,
    date: datetime.date | None = ...,
) -> tuple[datetime.date, Decimal] | tuple[None, None]: ...
