import datetime
import pytest

from fava.api import FavaAPIException


def test_context(example_api):
    assert example_api.context('NOHASH') == (None, None)
    entry, _ = example_api.context('4c452a1810af2dc53f644cdc558c4832')
    assert entry.narration == "Allowed contributions for one year"
    assert entry.date == datetime.date(2014, 1, 1)


def test_apiexception():
    with pytest.raises(FavaAPIException) as exception:
        raise FavaAPIException('error')
    exception = exception.value
    assert str(exception) == 'error'
    assert str(exception) == exception.message


def test_accounts(example_api):
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
