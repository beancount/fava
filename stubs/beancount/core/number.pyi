# pylint: disable=missing-docstring,unused-argument,multiple-statements
import decimal

Decimal = decimal.Decimal
ZERO: Decimal
HALF: Decimal
ONE: Decimal

class MISSING: ...

NUMBER_RE: str

def D(strord: Decimal | str | float | None = ...) -> Decimal: ...
def round_to(number: Decimal, increment: Decimal) -> Decimal: ...
def same_sign(number1: Decimal, number2: Decimal) -> bool: ...
