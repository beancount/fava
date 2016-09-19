from fava.util.excel import to_csv, to_excel


def test_to_csv(example_api):
    types, rows = example_api.query('balances', numberify=True)
    assert to_csv(types, rows)
    types, rows = example_api.query('select account, tags, date, day',
                                    numberify=True)
    assert to_csv(types, rows)


def test_to_excel(example_api):
    types, rows = example_api.query('balances', numberify=True)
    assert to_excel(types, rows, 'ods', 'balances')
