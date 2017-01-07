from beancount.query.query import run_query
from fava.util.excel import to_csv, to_excel


def test_to_csv(example_ledger):
    types, rows = run_query(example_ledger.all_entries, example_ledger.options,
                            'balances', numberify=True)
    assert to_csv(types, rows)
    types, rows = run_query(example_ledger.all_entries, example_ledger.options,
                            'select account, tags, date, day', numberify=True)
    assert to_csv(types, rows)


def test_to_excel(example_ledger):
    types, rows = run_query(example_ledger.all_entries, example_ledger.options,
                            'balances', numberify=True)
    assert to_excel(types, rows, 'ods', 'balances')
