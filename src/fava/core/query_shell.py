"""For using the Beancount shell from Fava."""

from __future__ import annotations

import contextlib
import datetime
import io
import textwrap
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from beancount.core.amount import Amount
from beancount.core.inventory import Inventory
from beancount.core.position import Position
from beancount.parser.options import OPTIONS_DEFAULTS
from beancount.query import query_compile
from beancount.query.query_compile import CompilationError
from beancount.query.query_parser import ParseError
from beancount.query.query_parser import RunCustom
from beancount.query.shell import BQLShell  # type: ignore[import-untyped]

from fava.beans.funcs import execute_query
from fava.beans.funcs import run_query
from fava.core.conversion import simple_units
from fava.core.module_base import FavaModule
from fava.helpers import FavaAPIError
from fava.util.excel import HAVE_EXCEL
from fava.util.excel import to_csv
from fava.util.excel import to_excel

if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal
    from typing import TypeVar

    from fava.beans.abc import Directive
    from fava.beans.abc import Query
    from fava.beans.funcs import QueryResult
    from fava.beans.funcs import ResultRow
    from fava.beans.funcs import ResultType
    from fava.core import FavaLedger
    from fava.core.inventory import SimpleCounterInventory
    from fava.helpers import BeancountError

    T = TypeVar("T")

    QueryRowValue = (
        bool | int | str | datetime.date | Decimal | Position | Inventory
    )
    SerialisedQueryRowValue = (
        bool
        | int
        | str
        | datetime.date
        | Decimal
        | Position
        | SimpleCounterInventory
    )

# This is to limit the size of the history file. Fava is not using readline at
# all, but Beancount somehow still is...
try:
    import readline

    readline.set_history_length(1000)
except ImportError:  # pragma: no cover
    pass


@dataclass(frozen=True)
class QueryResultTable:
    """Table query result."""

    types: list[BaseColumn]
    rows: list[tuple[SerialisedQueryRowValue, ...]]
    t: Literal["table"] = "table"


@dataclass(frozen=True)
class QueryResultText:
    """Text query result."""

    contents: str
    t: Literal["string"] = "string"


class QueryShell(BQLShell, FavaModule):  # type: ignore[misc]
    """A light wrapper around Beancount's shell."""

    def __init__(self, ledger: FavaLedger) -> None:
        self.buffer = io.StringIO()
        BQLShell.__init__(
            self,
            is_interactive=False,
            loadfun=None,
            outfile=self.buffer,
        )
        FavaModule.__init__(self, ledger)
        self.result: QueryResult | None = None
        self.stdout = self.buffer
        self.entries: list[Directive] = []
        self.errors: list[BeancountError] = []
        self.options_map = OPTIONS_DEFAULTS

    @property
    def queries(self) -> list[Query]:
        """All queries in the ledger."""
        return self.ledger.all_entries_by_type.Query

    def add_help(self) -> None:
        """Attach help functions for each of the parsed token handlers."""
        for attrname, func in BQLShell.__dict__.items():
            if attrname[:3] != "on_":
                continue
            command_name = attrname[3:]
            setattr(
                self.__class__,
                f"help_{command_name.lower()}",
                lambda _, fun=func: print(
                    textwrap.dedent(fun.__doc__).strip(),
                    file=self.buffer,
                ),
            )

    def get_pager(self) -> io.StringIO:
        """No real pager, just self.buffer to print to."""
        raise NotImplementedError
        # maybe we should return self.buffer

    def noop(self, _: T) -> None:
        """Doesn't do anything in Fava's query shell."""
        print(self.noop.__doc__, file=self.buffer)

    on_Reload = noop  # noqa: N815
    do_exit = noop
    do_quit = noop
    do_EOF = noop  # noqa: N815

    def on_Select(self, statement: str) -> None:  # noqa: D102, N802
        try:
            c_query = query_compile.compile(  # type: ignore[attr-defined]
                statement,
                self.env_targets,
                self.env_postings,
                self.env_entries,
            )
        except CompilationError as exc:
            print(f"ERROR: {str(exc).rstrip('.')}.", file=self.buffer)
            return
        rtypes, rrows = execute_query(c_query, self.entries, self.options_map)

        if not rrows:
            print("(empty)", file=self.buffer)

        self.result = rtypes, rrows

    def execute_query(
        self, entries: list[Directive], query: str
    ) -> (
        tuple[str, None, None] | tuple[None, list[ResultType], list[ResultRow]]
    ):
        """Run a query.

        Arguments:
            entries: The entries to run the query on.
            query: A query string.

        Returns:
            A tuple (contents, types, rows) where either the first or the last
            two entries are None. If the query result is a table, it will be
            contained in ``types`` and ``rows``, otherwise the result will be
            contained in ``contents`` (as a string).
        """
        self.entries = entries
        self.errors = self.ledger.errors
        self.options_map = self.ledger.options
        with contextlib.redirect_stdout(self.buffer):
            self.onecmd(query)
        contents = self.buffer.getvalue()
        self.buffer.truncate(0)
        if self.result is None:
            return (contents.strip().strip("\x00"), None, None)
        types, rows = self.result
        self.result = None
        return (None, types, rows)

    def execute_query_serialised(
        self, entries: list[Directive], query: str
    ) -> QueryResultTable | QueryResultText:
        """Run a query and returns its serialised result.

        Arguments:
            entries: The entries to run the query on.
            query: A query string.

        Returns:
            Either a table or a text result (depending on the query).
        """
        contents, types, rows = self.execute_query(entries, query)
        if contents and "ERROR" in contents:
            raise FavaAPIError(contents)

        if not types or not rows:
            return QueryResultText(contents or "")

        return QueryResultTable(*serialise_query_result(types, rows))

    def on_RunCustom(self, run_stmt: RunCustom) -> None:  # noqa: N802
        """Run a custom query."""
        name = run_stmt.query_name
        if name is None:
            # List the available queries.
            for query in self.queries:
                print(query.name, file=self.buffer)
        else:
            try:
                query = next(
                    query for query in self.queries if query.name == name
                )
            except StopIteration:
                print(f"ERROR: Query '{name}' not found", file=self.buffer)
            else:
                statement = self.parser.parse(query.query_string)
                self.dispatch(statement)

    def query_to_file(
        self,
        entries: list[Directive],
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

        try:
            statement = self.parser.parse(query_string)
        except ParseError as exception:
            raise FavaAPIError(str(exception)) from exception

        if isinstance(statement, RunCustom):
            name = statement.query_name

            try:
                query = next(
                    query for query in self.queries if query.name == name
                )
            except StopIteration as exc:
                msg = f'Query "{name}" not found.'
                raise FavaAPIError(msg) from exc
            query_string = query.query_string

        try:
            types, rows = run_query(
                entries,
                self.ledger.options,
                query_string,
                numberify=True,
            )
        except (CompilationError, ParseError) as exception:
            raise FavaAPIError(str(exception)) from exception

        if result_format == "csv":
            data = to_csv(types, rows)
        else:
            if not HAVE_EXCEL:
                msg = "Result format not supported."
                raise FavaAPIError(msg)
            data = to_excel(types, rows, result_format, query_string)
        return name, data


QueryShell.on_Select.__doc__ = BQLShell.on_Select.__doc__


@dataclass(frozen=True)
class BaseColumn:
    """A query column."""

    name: str
    dtype: str

    @staticmethod
    def serialise(
        val: QueryRowValue,
    ) -> SerialisedQueryRowValue:
        """Serialiseable version of the column value."""
        return val  # type: ignore[return-value]


@dataclass(frozen=True)
class BoolColumn(BaseColumn):
    """A boolean query column."""

    dtype: str = "bool"


@dataclass(frozen=True)
class DecimalColumn(BaseColumn):
    """A Decimal query column."""

    dtype: str = "Decimal"


@dataclass(frozen=True)
class IntColumn(BaseColumn):
    """A int query column."""

    dtype: str = "int"


@dataclass(frozen=True)
class StrColumn(BaseColumn):
    """A str query column."""

    dtype: str = "str"


@dataclass(frozen=True)
class DateColumn(BaseColumn):
    """A date query column."""

    dtype: str = "date"


@dataclass(frozen=True)
class PositionColumn(BaseColumn):
    """A Position query column."""

    dtype: str = "Position"


@dataclass(frozen=True)
class SetColumn(BaseColumn):
    """A set query column."""

    dtype: str = "set"


@dataclass(frozen=True)
class AmountColumn(BaseColumn):
    """An amount query column."""

    dtype: str = "Amount"


@dataclass(frozen=True)
class ObjectColumn(BaseColumn):
    """An object query column."""

    dtype: str = "object"

    @staticmethod
    def serialise(val: object) -> str:
        """Serialise an object of unknown type to a string."""
        return str(val)


@dataclass(frozen=True)
class InventoryColumn(BaseColumn):
    """A str query column."""

    dtype: str = "Inventory"

    @staticmethod
    def serialise(val: Inventory) -> SimpleCounterInventory:  # type: ignore[override]
        """Serialise an inventory."""
        return simple_units(val)


COLUMNS = {
    Amount: AmountColumn,
    Decimal: DecimalColumn,
    Inventory: InventoryColumn,
    Position: PositionColumn,
    bool: BoolColumn,
    datetime.date: DateColumn,
    int: IntColumn,
    set: SetColumn,
    str: StrColumn,
    object: ObjectColumn,
}


def serialise_query_result(
    types: list[ResultType], rows: list[ResultRow]
) -> tuple[list[BaseColumn], list[tuple[SerialisedQueryRowValue, ...]]]:
    """Serialise the query result."""
    dtypes = [COLUMNS[dtype](name) for name, dtype in types]
    mappers = [d.serialise for d in dtypes]
    mapped_rows = [
        tuple(mapper(row[i]) for i, mapper in enumerate(mappers))
        for row in rows
    ]
    return dtypes, mapped_rows
