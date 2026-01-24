"""For running BQL queries in Fava."""

from __future__ import annotations

import io
import shlex
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.core.query import COLUMNS
from fava.core.query import ObjectColumn
from fava.core.query import QueryResultTable
from fava.core.query import QueryResultText
from fava.helpers import FavaAPIError
from fava.rustledger.query import CompilationError
from fava.rustledger.query import connect
from fava.rustledger.query import ParseError
from fava.rustledger.query import RLCursor
from fava.util.excel import HAVE_EXCEL
from fava.util.excel import to_csv
from fava.util.excel import to_excel

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from fava.beans.abc import Directive
    from fava.core import FavaLedger


class FavaShellError(FavaAPIError):
    """An error in the Fava BQL shell, will be turned into a string."""


class QueryNotFoundError(FavaShellError):
    """Query '{name}' not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Query '{name}' not found.")


class TooManyRunArgsError(FavaShellError):
    """Too many args to run: '{args}'."""

    def __init__(self, args: str) -> None:
        super().__init__(f"Too many args to run: '{args}'.")


class QueryCompilationError(FavaShellError):
    """Query compilation error."""

    def __init__(self, err: CompilationError) -> None:
        super().__init__(f"Query compilation error: {err!s}.")


class QueryParseError(FavaShellError):
    """Query parse error."""

    def __init__(self, err: ParseError) -> None:
        super().__init__(f"Query parse error: {err!s}.")


class NonExportableQueryError(FavaShellError):
    """Only queries that return a table can be printed to a file."""

    def __init__(self) -> None:
        super().__init__(
            "Only queries that return a table can be printed to a file."
        )


class FavaQueryRunner:
    """Runs BQL queries using rustledger."""

    def __init__(self, ledger: FavaLedger) -> None:
        self.ledger = ledger

    def run(
        self, entries: Sequence[Directive], query: str
    ) -> RLCursor | str:
        """Run a query, returning cursor or text result."""
        # Get the source from the ledger for queries
        source = getattr(self.ledger, "_source", None)

        # Create connection
        conn = connect(
            "rustledger:",
            entries=entries,
            errors=self.ledger.errors,
            options=self.ledger.options,
        )

        if source:
            conn.set_source(source)

        # Parse the query to handle special commands
        query = query.strip()
        query_lower = query.lower()

        # Handle noop commands (return fixed text)
        noop_doc = "Doesn't do anything in Fava's query shell."
        if query_lower in (".exit", ".quit", "exit", "quit"):
            return noop_doc

        # Handle .run or run command
        if query_lower.startswith((".run", "run")):
            # Check if it's just "run" or ".run" (list queries) or "run name"
            if query_lower in ("run", ".run") or query_lower.startswith(("run ", ".run ")):
                return self._handle_run(query, conn)

        # Handle help commands - return text
        if query_lower.startswith((".help", "help")):
            # ".help exit" or ".help <command>" returns noop doc
            if " " in query_lower:
                return noop_doc
            return self._help_text()

        # Handle .explain - return placeholder
        if query_lower.startswith((".explain", "explain")):
            return f"EXPLAIN: {query}"

        # Handle SELECT/BALANCES/JOURNAL queries
        try:
            return conn.execute(query)
        except ParseError as exc:
            raise QueryParseError(exc) from exc
        except CompilationError as exc:
            raise QueryCompilationError(exc) from exc

    def _handle_run(self, query: str, conn: connect) -> RLCursor | str:
        """Handle .run command to execute stored queries."""
        queries = self.ledger.all_entries_by_type.Query

        # Parse the run command
        parts = shlex.split(query)
        if len(parts) == 1:
            # Just "run" - list available queries
            return "\n".join(q.name for q in queries)

        if len(parts) > 2:
            raise TooManyRunArgsError(query)

        name = parts[1].rstrip(";")
        query_obj = next((q for q in queries if q.name == name), None)
        if query_obj is None:
            raise QueryNotFoundError(name)

        try:
            return conn.execute(query_obj.query_string)
        except ParseError as exc:
            raise QueryParseError(exc) from exc
        except CompilationError as exc:
            raise QueryCompilationError(exc) from exc

    def _help_text(self) -> str:
        """Return help text for the query shell."""
        return """Fava Query Shell

Commands:
  SELECT ...     Run a BQL SELECT query
  run <name>     Run a stored query by name
  run            List all stored queries
  help           Show this help message

Example queries:
  SELECT account, sum(position) GROUP BY account
  SELECT date, narration, position WHERE account ~ "Expenses"
"""


class QueryShell(FavaModule):
    """A Fava module to run BQL queries."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.runner = FavaQueryRunner(ledger)

    def execute_query_serialised(
        self, entries: Sequence[Directive], query: str
    ) -> QueryResultTable | QueryResultText:
        """Run a query and returns its serialised result.

        Arguments:
            entries: The entries to run the query on.
            query: A query string.

        Returns:
            Either a table or a text result (depending on the query).

        Raises:
            FavaAPIError: If the query response is an error.
        """
        res = self.runner.run(entries, query)
        return (
            QueryResultText(res) if isinstance(res, str) else _serialise(res)
        )

    def query_to_file(
        self,
        entries: Sequence[Directive],
        query_string: str,
        result_format: str,
    ) -> tuple[str, io.BytesIO]:
        """Get query result as file.

        Arguments:
            entries: The entries to run the query on.
            query_string: A string, the query to run.
            result_format: The file format to save to.

        Returns:
            A tuple (name, data), where name is either 'query_result' or the
            name of a custom query if the query string is 'run name_of_query'.
            ``data`` contains the file contents.

        Raises:
            FavaAPIError: If the result format is not supported or the
            query failed.
        """
        name = "query_result"

        if query_string.lower().startswith((".run", "run ")):
            parts = shlex.split(query_string)
            if len(parts) > 2:
                raise TooManyRunArgsError(query_string)
            if len(parts) == 2:
                name = parts[1].rstrip(";")
                queries = self.ledger.all_entries_by_type.Query
                query_obj = next((q for q in queries if q.name == name), None)
                if query_obj is None:
                    raise QueryNotFoundError(name)
                query_string = query_obj.query_string

        res = self.runner.run(entries, query_string)
        if isinstance(res, str):
            raise NonExportableQueryError

        rrows = res.fetchall()
        rtypes = res.description

        # Convert rows to exportable format
        rows = _numberify_rows(rrows, rtypes)

        if result_format == "csv":
            data = to_csv(list(rtypes), rows)
        else:
            if not HAVE_EXCEL:  # pragma: no cover
                msg = "Result format not supported."
                raise FavaAPIError(msg)
            data = to_excel(list(rtypes), rows, result_format, query_string)
        return name, data


def _numberify_rows(
    rows: list[tuple],
    columns: tuple,
) -> list[tuple]:
    """Convert row values to exportable format.

    This replaces beanquery.numberify.numberify_results for our use case.
    """
    result = []
    for row in rows:
        new_row = []
        for i, value in enumerate(row):
            col = columns[i]
            # Convert complex types to strings for export
            if hasattr(value, "number") and hasattr(value, "currency"):
                # Amount-like
                new_row.append(f"{value.number} {value.currency}")
            elif isinstance(value, dict):
                # Inventory or other dict
                if "positions" in value:
                    # Inventory
                    parts = []
                    for pos in value.get("positions", []):
                        units = pos.get("units", {})
                        parts.append(f"{units.get('number', '')} {units.get('currency', '')}")
                    new_row.append(", ".join(parts))
                else:
                    new_row.append(str(value))
            elif isinstance(value, (list, set, frozenset)):
                new_row.append(", ".join(str(v) for v in value))
            else:
                new_row.append(value)
        result.append(tuple(new_row))
    return result


def _serialise(cursor: RLCursor) -> QueryResultTable:
    """Serialise the query result."""
    dtypes = [
        COLUMNS.get(c.datatype, ObjectColumn)(c.name)
        for c in cursor.description
    ]
    mappers = [d.serialise for d in dtypes]
    mapped_rows = [
        tuple(mapper(row[i]) for i, mapper in enumerate(mappers))
        for row in cursor
    ]
    return QueryResultTable(dtypes, mapped_rows)
