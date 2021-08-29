# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Tuple

from beancount.core.data import Entries

def parse_string(string: str) -> Tuple[Entries, None, None]: ...
