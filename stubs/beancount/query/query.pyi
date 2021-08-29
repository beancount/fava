# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from beancount.core.data import Entries

ResultType = Tuple[str, Type[Any]]
ResultRow = Tuple[Any, ...]

def run_query(
    entries: Entries,
    options_map: Any,
    query: str,
    numberify: Optional[bool] = None,
) -> Tuple[List[ResultType], List[ResultRow]]: ...
