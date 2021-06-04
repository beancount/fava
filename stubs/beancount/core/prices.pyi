# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from beancount.core.data import Entries
from beancount.core.number import Decimal

# def get_last_price_entries(entries: Any, date: Any): ...

BaseQuote = Tuple[str, str]
_DateAndPrice = Tuple[datetime.date, Decimal]

class PriceMap(Dict[Tuple[str, str], _DateAndPrice]):
    forward_pairs: List[BaseQuote]

def build_price_map(entries: Entries) -> PriceMap: ...

# def normalize_base_quote(base_quote: Any): ...
def get_all_prices(
    price_map: PriceMap, base_quote: BaseQuote
) -> List[_DateAndPrice]: ...

# def get_latest_price(price_map: Any, base_quote: Any): ...
def get_price(
    price_map: PriceMap,
    base_quote: BaseQuote,
    date: Optional[datetime.date] = ...,
) -> Union[Tuple[datetime.date, Decimal], Tuple[None, None]]: ...
