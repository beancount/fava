# pylint: disable=all
# flake8: noqa
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import NamedTuple

from beancount.core.data import Entries

class ParseError(Exception): ...

class RunCustom(NamedTuple):
    query_name: str
