from typing import Any
from typing import NamedTuple

from fava.helpers import BeancountError

class ParserError(BeancountError): ...

class ValueType(NamedTuple):
    value: Any
    dtype: Any
