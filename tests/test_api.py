def test_accounts(example_api):
    assert len(example_api.all_accounts) == 91
    assert len(example_api.all_accounts_leaf_only) == 54
    assert 'Assets' not in example_api.all_accounts_leaf_only
