from collections.abc import Iterator
from collections.abc import Sequence
from typing import Any

from fava.beans.types import BeancountOptions

class CompilationError(Exception): ...
class ParseError(Exception): ...

class Column:
    # This has more attributes in beanquery, we currently use just the two.

    name: str
    datatype: type[Any]

class Cursor:
    description: Sequence[Column]

    def fetchall(self) -> Sequence[tuple[Any, ...]]: ...
    def __iter__(self) -> Iterator[tuple[Any, ...]]: ...

class Connection:
    def execute(self, query: str) -> Cursor: ...

def connect(
    dsn: str,
    *,
    entries: Sequence[Any],
    options: BeancountOptions,
    errors: Sequence[Any],
) -> Connection: ...
