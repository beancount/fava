"""For using the Beancount shell from Fava."""

from __future__ import annotations

import contextlib
import io
import textwrap
from typing import Any
from typing import TYPE_CHECKING

from beancount.parser.options import OPTIONS_DEFAULTS
from beancount.query import query_compile
from beancount.query.query_compile import CompilationError
from beancount.query.query_parser import ParseError
from beancount.query.query_parser import RunCustom
from beancount.query.shell import BQLShell  # type: ignore[import-untyped]
from beancount.utils import pager  # type: ignore[attr-defined]

from fava.beans.funcs import execute_query
from fava.beans.funcs import run_query
from fava.core.module_base import FavaModule
from fava.helpers import FavaAPIError
from fava.util.excel import HAVE_EXCEL
from fava.util.excel import to_csv
from fava.util.excel import to_excel

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.beans.abc import Query
    from fava.beans.funcs import QueryResult
    from fava.core import FavaLedger
    from fava.helpers import BeancountError

# This is to limit the size of the history file. Fava is not using readline at
# all, but Beancount somehow still is...
try:
    import readline

    readline.set_history_length(1000)
except ImportError:
    pass


class QueryShell(BQLShell, FavaModule):  # type: ignore[misc]
    """A light wrapper around Beancount's shell."""

    def __init__(self, ledger: FavaLedger) -> None:
        self.buffer = io.StringIO()
        BQLShell.__init__(
            self,
            is_interactive=True,
            loadfun=None,
            outfile=self.buffer,
        )
        FavaModule.__init__(self, ledger)
        self.result: QueryResult | None = None
        self.stdout = self.buffer
        self.entries: list[Directive] = []
        self.errors: list[BeancountError] = []
        self.options_map = OPTIONS_DEFAULTS
        self.queries: list[Query] = []

    def load_file(self) -> None:
        self.queries = self.ledger.all_entries_by_type.Query

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

    def _loadfun(self) -> None:
        self.entries = self.ledger.all_entries
        self.errors = self.ledger.errors
        self.options_map = self.ledger.options

    def get_pager(self) -> Any:
        """No real pager, just a wrapper that doesn't close self.buffer."""
        return pager.flush_only(self.buffer)

    def noop(self, _: Any) -> None:
        """Doesn't do anything in Fava's query shell."""
        print(self.noop.__doc__, file=self.buffer)

    on_Reload = noop  # noqa: N815
    do_exit = noop
    do_quit = noop
    do_EOF = noop  # noqa: N815

    def on_Select(self, statement: str) -> None:  # noqa: N802
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

    def execute_query(self, entries: list[Directive], query: str) -> Any:
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
        self._loadfun()
        self.entries = entries
        with contextlib.redirect_stdout(self.buffer):
            self.onecmd(query)
        contents = self.buffer.getvalue()
        self.buffer.truncate(0)
        if self.result is None:
            return (contents.strip().strip("\x00"), None, None)
        types, rows = self.result
        self.result = None
        return (None, types, rows)

    def on_RunCustom(self, run_stmt: RunCustom) -> Any:  # noqa: N802
        """Run a custom query."""
        name = run_stmt.query_name
        if name is None:
            # List the available queries.
            for query in self.queries:
                print(query.name)  # noqa: T201
        else:
            try:
                query = next(
                    query for query in self.queries if query.name == name
                )
            except StopIteration:
                print(f"ERROR: Query '{name}' not found")  # noqa: T201
            else:
                statement = self.parser.parse(query.query_string)
                self.dispatch(statement)

    def query_to_file(
        self,
        entries: list[Directive],
        query_string: str,
        result_format: str,
    ) -> Any:
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
                raise FavaAPIError(f'Query "{name}" not found.') from exc
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
                raise FavaAPIError("Result format not supported.")
            data = to_excel(types, rows, result_format, query_string)
        return name, data


QueryShell.on_Select.__doc__ = BQLShell.on_Select.__doc__
