import datetime
import pytest

from fava.core import FavaAPIException


def test_context(example_ledger):
    entry, _ = example_ledger.context('4c452a1810af2dc53f644cdc558c4832')
    assert entry.narration == "Allowed contributions for one year"
    assert entry.date == datetime.date(2014, 1, 1)

    with pytest.raises(FavaAPIException):
        example_ledger.context('NOHASH')


def test_apiexception():
    with pytest.raises(FavaAPIException) as exception:
        raise FavaAPIException('error')
    exception = exception.value
    assert str(exception) == 'error'
    assert str(exception) == exception.message


def test_attributes(example_ledger):
    assert len(example_ledger.attributes.accounts) == 61
    assert 'Assets' not in example_ledger.attributes.accounts


def test_account_metadata(example_ledger):
    data = example_ledger.account_metadata('Assets:US:BofA')
    assert data['address'] == "123 America Street, LargeTown, USA"
    assert data['institution'] == "Bank of America"

    assert not example_ledger.account_metadata('Assets')

    assert not example_ledger.account_metadata('NOACCOUNT')


def test_account_uptodate_status(example_ledger):
    status = example_ledger.account_uptodate_status('Assets:US:BofA')
    assert not status

    status = example_ledger.account_uptodate_status('Assets:US:BofA:Checking')
    assert status == 'yellow'

    status = example_ledger.account_uptodate_status(
        'Liabilities:US:Chase:Slate')
    assert status == 'green'
