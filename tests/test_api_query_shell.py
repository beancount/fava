import os

from beancount.query import query
import pytest

from fava.core.helpers import FavaAPIException
from fava.core.query_shell import QueryShell


def test_execute_query(example_ledger):
    query_shell = QueryShell(example_ledger)

    assert query_shell.execute_query('help exit') == \
        (QueryShell.noop.__doc__ + '\n', None, None)

    assert query_shell.execute_query('help')[1:] == \
        (None, None)

    assert query_shell.execute_query('balances')[1:] == \
        query.run_query(query_shell.entries, query_shell.options_map,
                        'balances')

    assert query_shell.get_history(3) == ['help exit', 'help', 'balances']


def test_query_to_file(example_ledger, tmpdir):
    query_shell = QueryShell(example_ledger)

    name, data = query_shell.query_to_file('balances', 'csv')
    assert name == 'query_result'
    csv = os.path.join(os.path.dirname(__file__), 'data/example-balances.csv')
    with open(csv, 'rb') as file:
        assert data.getvalue() == file.read()

    with pytest.raises(FavaAPIException):
        query_shell.query_to_file('select sdf', 'csv')

    with pytest.raises(FavaAPIException):
        query_shell.query_to_file('run testsetest', 'csv')

    # name, data1 = query_shell.query_to_file('run fava', 'csv')
    # _, data2 = query_shell.query_to_file('journal', 'csv')
    # assert name == 'fava'
    # assert data1.getvalue() == data2.getvalue()
