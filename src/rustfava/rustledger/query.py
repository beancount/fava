"""Query adapter for rustledger - replaces beanquery."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from rustfava.rustledger.engine import RustledgerEngine
from rustfava.rustledger.types import RLAmount

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Sequence
    from typing import Any

    from rustfava.beans.abc import Directive
    from rustfava.beans.types import BeancountOptions
    from rustfava.helpers import BeancountError


@dataclass
class ColumnDescription:
    """Description of a query result column.

    Compatible with beanquery's column description.
    """

    name: str
    datatype: type

    def __iter__(self) -> Iterator[Any]:
        """Allow tuple unpacking."""
        yield self.name
        yield self.datatype


class RLCursor:
    """Cursor for rustledger query results.

    Compatible with beanquery.Cursor interface.
    """

    def __init__(
        self,
        columns: list[dict[str, str]],
        rows: list[list[Any]],
    ) -> None:
        """Initialize cursor with query results."""
        self._columns = columns
        self._rows = rows
        self._index = 0

        # Build description (like DB-API cursor.description)
        self.description = tuple(
            ColumnDescription(
                name=col["name"],
                datatype=_datatype_from_string(col.get("datatype", "object")),
            )
            for col in columns
        )

    def fetchall(self) -> list[tuple[Any, ...]]:
        """Fetch all remaining rows."""
        rows = [
            tuple(_convert_row_value(v, self._columns[i]) for i, v in enumerate(row))
            for row in self._rows[self._index :]
        ]
        self._index = len(self._rows)
        return rows

    def fetchone(self) -> tuple[Any, ...] | None:
        """Fetch next row."""
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return tuple(
            _convert_row_value(v, self._columns[i]) for i, v in enumerate(row)
        )

    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        """Iterate over rows."""
        for row in self._rows[self._index :]:
            yield tuple(
                _convert_row_value(v, self._columns[i]) for i, v in enumerate(row)
            )


# Type mapping from rustledger strings to Python types
_DATATYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "Decimal": Decimal,
    "bool": bool,
    "date": str,  # Keep as string, Fava handles conversion
    "set": frozenset,
    "object": object,
    "Amount": RLAmount,
    "Position": object,
    "Inventory": dict,
}


def _datatype_from_string(datatype: str) -> type:
    """Convert datatype string to Python type."""
    return _DATATYPE_MAP.get(datatype, object)


def _convert_row_value(value: Any, column: dict[str, str]) -> Any:
    """Convert a row value based on column type."""
    if value is None:
        return None

    datatype = column.get("datatype", "object")

    if datatype == "Decimal" and isinstance(value, str):
        return Decimal(value)
    if datatype == "Amount" and isinstance(value, dict):
        return RLAmount.from_json(value)
    if datatype == "set" and isinstance(value, list):
        return frozenset(value)
    if datatype == "Inventory" and isinstance(value, dict):
        # Inventory comes as {"positions": [{"units": {"number": "...", "currency": "..."}}]}
        # Convert to simpler format for Fava
        positions = value.get("positions", [])
        result = {}
        for pos in positions:
            units = pos.get("units", {})
            currency = units.get("currency", "")
            number = units.get("number", "0")
            if currency:
                result[currency] = Decimal(number)
        return result

    return value


class RLQueryError(Exception):
    """Error from rustledger query execution."""


class ParseError(RLQueryError):
    """BQL parse error."""


class CompilationError(RLQueryError):
    """BQL compilation error."""


def connect(
    connection_string: str,
    entries: Sequence[Directive],
    errors: Sequence[BeancountError],
    options: BeancountOptions,
) -> RLConnection:
    """Create a connection for running queries.

    This matches beanquery.connect() interface.

    Args:
        connection_string: Ignored (beancount: prefix for compatibility)
        entries: List of directives
        errors: List of errors (ignored)
        options: Beancount options

    Returns:
        A connection object for executing queries
    """
    return RLConnection(entries, options)


class RLConnection:
    """Connection for executing BQL queries against entries.

    Unlike the beancount approach that re-serializes entries,
    we directly call rustledger with the original source.
    This requires the source to be stored or re-read.
    """

    def __init__(
        self,
        entries: Sequence[Directive],
        options: BeancountOptions,
    ) -> None:
        """Initialize connection."""
        self._entries = entries
        self._options = options
        self._engine = RustledgerEngine.get_instance()
        self._source: str | None = None

    def set_source(self, source: str) -> None:
        """Set the source for queries.

        Since rustledger queries operate on source text (not serialized entries),
        we need the original source.
        """
        self._source = source

    def execute(self, query_string: str) -> RLCursor:
        """Execute a BQL query.

        Args:
            query_string: BQL query string

        Returns:
            A cursor with query results

        Raises:
            ParseError: If the query cannot be parsed
            CompilationError: If the query cannot be compiled
            RuntimeError: If source is not set
        """
        if self._source is None:
            # Fall back to re-serializing entries (slower but works)
            self._source = _entries_to_source(self._entries)

        result = self._engine.query(self._source, query_string)

        errors = result.get("errors", [])
        if errors:
            error_msg = errors[0].get("message", "Unknown error")
            if "parse" in error_msg.lower():
                raise ParseError(error_msg)
            raise CompilationError(error_msg)

        return RLCursor(
            columns=result.get("columns", []),
            rows=result.get("rows", []),
        )


def _entries_to_source(entries: Sequence[Directive]) -> str:
    """Convert entries back to beancount source for querying.

    This is a fallback when the original source isn't available.
    """
    lines = []
    for entry in entries:
        line = _directive_to_source(entry)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _directive_to_source(directive: Directive) -> str:
    """Convert a directive to beancount source line."""
    date = directive.date.isoformat()
    dtype = type(directive).__name__.lower().replace("rl", "")

    if dtype == "open":
        currencies = " ".join(getattr(directive, "currencies", []))
        return f'{date} open {directive.account} {currencies}'.strip()

    if dtype == "close":
        return f'{date} close {directive.account}'

    if dtype == "balance":
        amt = directive.amount
        return f'{date} balance {directive.account} {amt.number} {amt.currency}'

    if dtype == "transaction":
        flag = getattr(directive, "flag", "*")
        payee = getattr(directive, "payee", None)
        narration = getattr(directive, "narration", "")

        if payee:
            header = f'{date} {flag} "{payee}" "{narration}"'
        else:
            header = f'{date} {flag} "{narration}"'

        posting_lines = []
        for p in directive.postings:
            if p.units:
                posting_lines.append(f'  {p.account}  {p.units.number} {p.units.currency}')
            else:
                posting_lines.append(f'  {p.account}')

        return header + "\n" + "\n".join(posting_lines)

    if dtype == "price":
        amt = directive.amount
        return f'{date} price {directive.currency} {amt.number} {amt.currency}'

    if dtype == "commodity":
        return f'{date} commodity {directive.currency}'

    if dtype == "event":
        event_type = getattr(directive, "type", "")
        desc = getattr(directive, "description", "")
        return f'{date} event "{event_type}" "{desc}"'

    if dtype == "note":
        comment = getattr(directive, "comment", "")
        return f'{date} note {directive.account} "{comment}"'

    if dtype == "document":
        filename = getattr(directive, "filename", "")
        return f'{date} document {directive.account} "{filename}"'

    if dtype == "pad":
        source_account = getattr(directive, "source_account", "")
        return f'{date} pad {directive.account} {source_account}'

    if dtype == "query":
        name = getattr(directive, "name", "")
        query_string = getattr(directive, "query_string", "")
        return f'{date} query "{name}" "{query_string}"'

    if dtype == "custom":
        # Skip fava-specific custom directives that rustledger can't parse
        custom_type = getattr(directive, "type", "")
        if custom_type.startswith("fava"):
            return ""
        values = getattr(directive, "values", [])
        values_str = " ".join(f'"{v}"' for v in values)
        return f'{date} custom "{custom_type}" {values_str}'

    return ""
