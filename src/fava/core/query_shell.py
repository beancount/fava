"""For using the Beancount shell from Fava."""
# mypy: ignore-errors
import contextlib
import io
import textwrap
from typing import List
from typing import TYPE_CHECKING

from beancount.core.data import Entries
from beancount.core.data import Query
from beancount.parser.options import OPTIONS_DEFAULTS
from beancount.query import query_compile
from beancount.query.query import run_query
from beancount.query.query_compile import CompilationError
from beancount.query.query_execute import execute_query
from beancount.query.query_parser import ParseError
from beancount.query.query_parser import RunCustom
from beancount.query.shell import BQLShell  # type: ignore
from beancount.utils import pager  # type: ignore

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.helpers import FavaAPIException
from fava.util.excel import HAVE_EXCEL
from fava.util.excel import to_csv
from fava.util.excel import to_excel

if TYPE_CHECKING:
    from fava.core import FavaLedger

# This is to limit the size of the history file. Fava is not using readline at
# all, but Beancount somehow still is...
try:
    import readline

    readline.set_history_length(1000)
except ImportError:
    pass


class QueryShell(BQLShell, FavaModule):
    """A light wrapper around Beancount's shell."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, ledger: "FavaLedger"):
        self.buffer = io.StringIO()
        BQLShell.__init__(self, True, None, self.buffer)
        FavaModule.__init__(self, ledger)
        self.result = None
        self.stdout = self.buffer
        self.entries: Entries = []
        self.errors: List[BeancountError] = []
        self.options_map = OPTIONS_DEFAULTS
        self.queries: List[Query] = []

    def load_file(self) -> None:
        self.queries = self.ledger.all_entries_by_type.Query

    def add_help(self) -> None:
        "Attach help functions for each of the parsed token handlers."
        for attrname, func in BQLShell.__dict__.items():
            if attrname[:3] != "on_":
                continue
            command_name = attrname[3:]
            setattr(
                self.__class__,
                f"help_{command_name.lower()}",
                lambda _, fun=func: print(
                    textwrap.dedent(fun.__doc__).strip(), file=self.outfile
                ),
            )

    def _loadfun(self) -> None:
        self.entries = self.ledger.entries
        self.errors = self.ledger.errors
        self.options_map = self.ledger.options

    def get_pager(self):
        """No real pager, just a wrapper that doesn't close self.buffer."""
        return pager.flush_only(self.buffer)

    def noop(self, _) -> None:
        """Doesn't do anything in Fava's query shell."""
        print(self.noop.__doc__, file=self.outfile)

    on_Reload = noop
    do_exit = noop
    do_quit = noop
    do_EOF = noop

    def on_Select(self, statement):
        # pylint: disable=invalid-name
        try:
            c_query = query_compile.compile(
                statement,
                self.env_targets,
                self.env_postings,
                self.env_entries,
            )
        except CompilationError as exc:
            print(f"ERROR: {str(exc).rstrip('.')}.", file=self.outfile)
            return
        rtypes, rrows = execute_query(c_query, self.entries, self.options_map)

        if not rrows:
            print("(empty)", file=self.outfile)

        self.result = rtypes, rrows

    def execute_query(self, query: str):
        """Run a query.

        Arguments:
            query: A query string.

        Returns:
            A tuple (contents, types, rows) where either the first or the last
            two entries are None. If the query result is a table, it will be
            contained in ``types`` and ``rows``, otherwise the result will be
            contained in ``contents`` (as a string).
        """
        self._loadfun()
        with contextlib.redirect_stdout(self.buffer):
            self.onecmd(query)
        contents = self.buffer.getvalue()
        self.buffer.truncate(0)
        if self.result is None:
            return (contents.strip().strip("\x00"), None, None)
        types, rows = self.result
        self.result = None
        return (None, types, rows)

    def on_RunCustom(self, run_stmt):
        """Run a custom query."""
        name = run_stmt.query_name
        if name is None:
            # List the available queries.
            for query in self.queries:
                print(query.name)
        else:
            try:
                query = next(
                    query for query in self.queries if query.name == name
                )
            except StopIteration:
                print(f"ERROR: Query '{name}' not found")
            else:
                statement = self.parser.parse(query.query_string)
                self.dispatch(statement)

    def query_to_file(self, query_string: str, result_format: str):
        """Get query result as file.

        Arguments:
            query_string: A string, the query to run.
            result_format: The file format to save to.

        Returns:
            A tuple (name, data), where name is either 'query_result' or the
            name of a custom query if the query string is 'run name_of_query'.
            ``data`` contains the file contents.

        Raises:
            FavaAPIException: If the result format is not supported or the
            query failed.
        """
        name = "query_result"

        try:
            statement = self.parser.parse(query_string)
        except ParseError as exception:
            raise FavaAPIException(str(exception)) from exception

        if isinstance(statement, RunCustom):
            name = statement.query_name

            try:
                query = next(
                    query for query in self.queries if query.name == name
                )
            except StopIteration as exc:
                raise FavaAPIException(f'Query "{name}" not found.') from exc
            query_string = query.query_string

        try:
            types, rows = run_query(
                self.ledger.entries,
                self.ledger.options,
                query_string,
                numberify=True,
            )
        except (CompilationError, ParseError) as exception:
            raise FavaAPIException(str(exception)) from exception

        if result_format == "csv":
            data = to_csv(types, rows)
        else:
            if not HAVE_EXCEL:
                raise FavaAPIException("Result format not supported.")
            data = to_excel(types, rows, result_format, query_string)
        return name, data


QueryShell.on_Select.__doc__ = BQLShell.on_Select.__doc__
