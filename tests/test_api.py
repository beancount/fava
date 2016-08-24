def test_accounts(example_api):
    assert len(example_api.all_accounts) == 91
    assert len(example_api.all_accounts_active) == 59
    assert 'Assets' not in example_api.all_accounts_active


def test_linechart_data(example_api):
    data = example_api.linechart_data('Liabilities:AccountsPayable')
    assert len(data) == 6
    assert data[-1]['balance']['USD'] == 0
