# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Any
from typing import TypeAlias

from beancount.core.data import Entries

ResultType: TypeAlias = tuple[str, type[Any]]
ResultRow: TypeAlias = tuple[Any, ...]

def run_query(
    entries: Entries,
    options_map: Any,
    query: str,
    numberify: bool | None = ...,
) -> tuple[list[ResultType], list[ResultRow]]: ...
