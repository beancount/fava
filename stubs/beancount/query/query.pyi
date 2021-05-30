# pylint: disable=missing-docstring,unused-argument,multiple-statements

from typing import Any
from typing import List
from typing import Tuple
from typing import Type

from beancount.core.data import Entries

def run_query(
    entries: Entries, options_map: Any, query: str, numberify: bool = None
) -> Tuple[List[Type], List[Tuple]]: ...
