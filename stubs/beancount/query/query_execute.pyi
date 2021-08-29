# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import List
from typing import Tuple

from beancount.core.data import Entries
from beancount.query.query import ResultRow
from beancount.query.query import ResultType

from fava.util.typing import BeancountOptions

def execute_query(
    query: str, entries: Entries, options_map: BeancountOptions
) -> Tuple[List[ResultType], List[ResultRow]]: ...
