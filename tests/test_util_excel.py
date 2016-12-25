from beancount.query.query import run_query
from fava.util.excel import to_csv, to_excel


def test_to_csv(example_api):
    types, rows = run_query(example_api.all_entries, example_api.options,
                            'balances', numberify=True)
    assert to_csv(types, rows)
    types, rows = run_query(example_api.all_entries, example_api.options,
                            'select account, tags, date, day', numberify=True)
    assert to_csv(types, rows)


def test_to_excel(example_api):
    types, rows = run_query(example_api.all_entries, example_api.options,
                            'balances', numberify=True)
    assert to_excel(types, rows, 'ods', 'balances')
