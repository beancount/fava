# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Any
from typing import Type

from beancount.core.data import Entries

ResultType = tuple[str, Type[Any]]
ResultRow = tuple[Any, ...]

def run_query(
    entries: Entries,
    options_map: Any,
    query: str,
    numberify: bool | None = None,
) -> tuple[list[ResultType], list[ResultRow]]: ...
