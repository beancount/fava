"""Various functions to deal with Beancount data."""
from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

from beancount.core import compare  # type: ignore
from beancount.query import query  # type: ignore
from beancount.query import query_execute  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeAlias

    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions

    ResultType: TypeAlias = tuple[str, type[Any]]
    ResultRow: TypeAlias = tuple[Any, ...]
    QueryResult: TypeAlias = tuple[list[ResultType], list[ResultRow]]


def hash_entry(entry: Directive) -> str:
    """Hash an entry."""
    return compare.hash_entry(entry)  # type: ignore


def execute_query(
    query_: str, entries: list[Directive], options_map: BeancountOptions
) -> QueryResult:
    """Execture a query."""
    return query_execute.execute_query(query_, entries, options_map)  # type: ignore


def run_query(
    entries: list[Directive],
    options_map: Any,
    _query: str,
    numberify: bool = False,
) -> QueryResult:
    """Run a query."""
    return query.run_query(  # type: ignore
        entries,
        options_map,
        _query,
        numberify=numberify,
    )
