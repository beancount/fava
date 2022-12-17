# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime
from typing import TypeAlias

from beancount.core.data import Entries
from beancount.core.number import Decimal

# def get_last_price_entries(entries: Any, date: Any): ...

BaseQuote: TypeAlias = tuple[str, str]
_DateAndPrice: TypeAlias = tuple[datetime.date, Decimal]

class PriceMap(dict[tuple[str, str], _DateAndPrice]):
    forward_pairs: list[BaseQuote]

def build_price_map(entries: Entries) -> PriceMap: ...

# def normalize_base_quote(base_quote: Any): ...
def get_all_prices(
    price_map: PriceMap, base_quote: BaseQuote
) -> list[_DateAndPrice]: ...

# def get_latest_price(price_map: Any, base_quote: Any): ...
def get_price(
    price_map: PriceMap,
    base_quote: BaseQuote,
    date: datetime.date | None = ...,
) -> tuple[datetime.date, Decimal] | tuple[None, None]: ...
