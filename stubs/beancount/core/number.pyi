# pylint: disable=missing-docstring,unused-argument,multiple-statements
import decimal
from typing import Optional
from typing import Union

Decimal = decimal.Decimal
ZERO: Decimal
HALF: Decimal
ONE: Decimal

class MISSING: ...

NUMBER_RE: str

def D(strord: Optional[Union[Decimal, str, int, float]] = ...) -> Decimal: ...
def round_to(number: Decimal, increment: Decimal) -> Decimal: ...
def same_sign(number1: Decimal, number2: Decimal) -> bool: ...
