def test_accounts(example_api):
    assert len(example_api.all_accounts) == 93
    assert len(example_api.all_accounts_active) == 61
    assert 'Assets' not in example_api.all_accounts_active


def test_linechart_data(example_api):
    data = example_api.linechart_data('Assets:Testing:MultipleCommodities')
    assert data[1]['balance'].get('USD', None) == 50
    assert data[2]['balance'].get('USD', None) == 0
