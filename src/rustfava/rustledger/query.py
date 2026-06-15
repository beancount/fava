"""Query adapter for rustledger - replaces beanquery."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from rustfava.beans.str import to_string
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
        # The FFI payload carries units only -- no per-position cost basis -- so
        # this units-summed {currency: Decimal} form is the complete information
        # available for an inventory column. Cost basis / market value are
        # exposed separately via the COST()/VALUE() BQL functions (which return
        # scalar amounts). Preserving cost lots here would require the engine to
        # emit cost per position first; see rustledger/rustfava#155.
        positions = value.get("positions", [])
        result = {}
        for pos in positions:
            units = pos.get("units", {})
            currency = units.get("currency", "")
            number = units.get("number", "0")
            if currency:
                # Sum across lots: an inventory may hold several positions of
                # the same currency at different cost bases (now that the
                # serializer preserves cost). Flattening to {currency: number}
                # must accumulate, not overwrite, or all but one lot is lost.
                result[currency] = result.get(currency, Decimal(0)) + Decimal(
                    number
                )
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

    Delegates to ``rustfava.beans.str.to_string``, which is the same
    formatter rustfava uses elsewhere and handles tags, links, metadata,
    posting flags, cost basis, prices, booking methods, and balance
    tolerance. Custom directives whose type begins with ``fava`` are
    skipped because rledger cannot parse them.
    """
    parts: list[str] = []
    for entry in entries:
        if (
            type(entry).__name__ == "RLCustom"
            and getattr(entry, "type", "").startswith("fava")
        ):
            continue
        rendered = to_string(entry)
        if rendered:
            parts.append(rendered)
    return "\n".join(parts) + ("\n" if parts else "")
