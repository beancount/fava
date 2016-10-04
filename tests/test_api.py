def test_accounts(example_api):
    assert len(example_api.all_accounts) == 93
    assert len(example_api.all_accounts_active) == 61
    assert 'Assets' not in example_api.all_accounts_active


def test_account_metadata(example_api):
    data = example_api.account_metadata('Assets:US:BofA')
    assert data['address'] == "123 America Street, LargeTown, USA"
    assert data['institution'] == "Bank of America"

    assert not example_api.account_metadata('Assets')

    assert not example_api.account_metadata('NOACCOUNT')


def test_account_uptodate_status(example_api):
    status = example_api.account_uptodate_status('Assets:US:BofA')
    assert not status

    status = example_api.account_uptodate_status('Assets:US:BofA:Checking')
    assert status == 'yellow'

    status = example_api.account_uptodate_status('Liabilities:US:Chase:Slate')
    assert status == 'green'
