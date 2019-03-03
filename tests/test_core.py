# pylint: disable=missing-docstring

import os
import pytest

from fava.core import FavaAPIException


def test_apiexception():
    with pytest.raises(FavaAPIException) as exception:
        raise FavaAPIException("error")
    exception = exception.value
    assert str(exception) == "error"
    assert str(exception) == exception.message


def test_attributes(example_ledger):
    assert len(example_ledger.attributes.accounts) == 61
    assert "Assets" not in example_ledger.attributes.accounts


def test_paths_to_watch(example_ledger):
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [],
    )
    documents = example_ledger.options["documents"]
    example_ledger.options["documents"] = ["folder"]
    base = os.path.join(
        os.path.dirname(example_ledger.beancount_file_path), "folder"
    )
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [
            os.path.join(base, account)
            for account in [
                "Assets",
                "Liabilities",
                "Equity",
                "Income",
                "Expenses",
            ]
        ],
    )
    example_ledger.options["documents"] = documents


def test_account_metadata(example_ledger):
    data = example_ledger.accounts["Assets:US:BofA"].meta
    assert data["address"] == "123 America Street, LargeTown, USA"
    assert data["institution"] == "Bank of America"

    assert not example_ledger.accounts["Assets"].meta
    assert not example_ledger.accounts["NOACCOUNT"].meta


def test_account_uptodate_status(example_ledger):
    status = example_ledger.account_uptodate_status("Assets:US:BofA")
    assert not status

    status = example_ledger.account_uptodate_status("Assets:US:BofA:Checking")
    assert status == "yellow"

    status = example_ledger.account_uptodate_status(
        "Liabilities:US:Chase:Slate"
    )
    assert status == "green"
