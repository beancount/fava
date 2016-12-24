"""For using the Beancount shell from Fava."""

import contextlib
import io
import readline
import textwrap

from beancount.query import query_compile, query_execute, shell
from beancount.utils import pager


class QueryShell(shell.BQLShell):
    """A light wrapper around Beancount's shell."""

    def __init__(self, api):
        self.api = api
        self.buffer = io.StringIO()
        self.result = None
        super().__init__(True, None, self.buffer)
        self.stdout = self.buffer
        self.entries = None
        self.errors = None
        self.options_map = None

    def add_help(self):
        "Attach help functions for each of the parsed token handlers."
        for attrname, func in list(shell.BQLShell.__dict__.items()):
            if attrname[:3] != 'on_':
                continue
            command_name = attrname[3:]
            setattr(self.__class__, 'help_{}'.format(command_name.lower()),
                    lambda _, fun=func: print(textwrap.dedent(fun.__doc__).strip(),
                                              file=self.outfile))

    def get_history(self, max_entries):
        num_entries = readline.get_current_history_length()
        return [readline.get_history_item(index+1) for
                index in range(max(num_entries-max_entries, 0),
                               num_entries)]

    def _loadfun(self):
        self.entries = self.api.all_entries
        self.errors = self.api.errors
        self.options_map = self.api.options

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
            c_query = query_compile.compile(statement,
                                            self.env_targets,
                                            self.env_postings,
                                            self.env_entries)
        except query_compile.CompilationError as exc:
            print('ERROR: {}.'.format(str(exc).rstrip('.')), file=self.outfile)
            return
        rtypes, rrows = query_execute.execute_query(c_query,
                                                    self.entries,
                                                    self.options_map)

        if not rrows:
            print("(empty)", file=self.outfile)

        self.result = rtypes, rrows

    def execute_query(self, query):
        self._loadfun()
        with contextlib.redirect_stdout(self.buffer):
            self.onecmd(query)
        if query:
            readline.add_history(query)
        contents = self.buffer.getvalue()
        self.buffer.truncate(0)
        if not self.result:
            return (contents, None, None)
        types, rows = self.result
        self.result = None
        return (None, types, rows)


QueryShell.on_Select.__doc__ = shell.BQLShell.on_Select.__doc__
