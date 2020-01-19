"""For using the Beancount shell from Fava."""

import contextlib
import io
import readline
import textwrap

from beancount.core.data import Query
from beancount.query import query_compile, query_execute, query_parser, shell
from beancount.query.query import run_query
from beancount.utils import pager

from fava.core.helpers import FavaAPIException, FavaModule
from fava.util.excel import to_csv, to_excel, HAVE_EXCEL


# This is to limit the size of the history file. Fava is not using readline at
# all, but Beancount somehow still is...
readline.set_history_length(1000)


class QueryShell(shell.BQLShell, FavaModule):
    """A light wrapper around Beancount's shell."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, ledger):
        self.ledger = ledger
        self.buffer = io.StringIO()
        self.result = None
        super().__init__(True, None, self.buffer)
        self.stdout = self.buffer
        self.entries = None
        self.errors = None
        self.options_map = None
        self.queries = []

    def load_file(self):
        self.queries = self.ledger.all_entries_by_type[Query]

    def add_help(self):
        "Attach help functions for each of the parsed token handlers."
        for attrname, func in list(shell.BQLShell.__dict__.items()):
            if attrname[:3] != "on_":
                continue
            command_name = attrname[3:]
            setattr(
                self.__class__,
                "help_{}".format(command_name.lower()),
                lambda _, fun=func: print(
                    textwrap.dedent(fun.__doc__).strip(), file=self.outfile
                ),
            )

    def _loadfun(self):
        self.entries = self.ledger.entries
        self.errors = self.ledger.errors
        self.options_map = self.ledger.options

    def get_pager(self):
        """No real pager, just a wrapper that doesn't close self.buffer."""
        return pager.flush_only(self.buffer)

    def noop(self, _):
        """Doesn't do anything in Fava's query shell."""
        print(self.noop.__doc__, file=self.outfile)

    on_Reload = noop
    do_exit = noop
    do_quit = noop
    do_EOF = noop

    def on_Select(self, statement):  # pylint: disable=invalid-name
        try:
            c_query = query_compile.compile(
                statement,
                self.env_targets,
                self.env_postings,
                self.env_entries,
            )
        except query_compile.CompilationError as exc:
            print("ERROR: {}.".format(str(exc).rstrip(".")), file=self.outfile)
            return
        rtypes, rrows = query_execute.execute_query(
            c_query, self.entries, self.options_map
        )

        if not rrows:
            print("(empty)", file=self.outfile)

        self.result = rtypes, rrows

    def execute_query(self, query):
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
            return (contents, None, None)
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
                    (query for query in self.queries if query.name == name)
                )
            except StopIteration:
                print("ERROR: Query '{}' not found".format(name))
            else:
                statement = self.parser.parse(query.query_string)
                self.dispatch(statement)

    def query_to_file(self, query_string, result_format):
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
        except query_parser.ParseError as exception:
            raise FavaAPIException(str(exception))

        if statement.__class__.__name__ == "RunCustom":
            name = statement.query_name

            try:
                query = next(
                    (query for query in self.queries if query.name == name)
                )
            except StopIteration:
                raise FavaAPIException('Query "{}" not found.'.format(name))
            query_string = query.query_string

        try:
            types, rows = run_query(
                self.ledger.all_entries,
                self.ledger.options,
                query_string,
                numberify=True,
            )
        except (
            query_compile.CompilationError,
            query_parser.ParseError,
        ) as exception:
            raise FavaAPIException(str(exception))

        if result_format == "csv":
            data = to_csv(types, rows)
        else:
            if not HAVE_EXCEL:
                raise FavaAPIException("Result format not supported.")
            data = to_excel(types, rows, result_format, query_string)
        return name, data


QueryShell.on_Select.__doc__ = shell.BQLShell.on_Select.__doc__
