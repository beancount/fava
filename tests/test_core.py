# pylint: disable=missing-docstring
from pathlib import Path

import pytest

from fava.core import FavaAPIException
from fava.core import FavaLedger


def test_apiexception():
    with pytest.raises(FavaAPIException) as exception:
        raise FavaAPIException("error")
    exception = exception.value
    assert str(exception) == "error"
    assert str(exception) == exception.message


def test_attributes(example_ledger: FavaLedger) -> None:
    assert len(example_ledger.attributes.accounts) == 61
    assert "Assets" not in example_ledger.attributes.accounts


def test_paths_to_watch(example_ledger: FavaLedger) -> None:
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [],
    )
    example_ledger.options["documents"] = ["folder"]
    base = Path(example_ledger.beancount_file_path).parent / "folder"
    assert example_ledger.paths_to_watch() == (
        [example_ledger.beancount_file_path],
        [
            str(base / account)
            for account in [
                "Assets",
                "Liabilities",
                "Equity",
                "Income",
                "Expenses",
            ]
        ],
    )


def test_account_metadata(example_ledger: FavaLedger) -> None:
    data = example_ledger.accounts["Assets:US:BofA"].meta
    assert data["address"] == "123 America Street, LargeTown, USA"
    assert data["institution"] == "Bank of America"

    assert not example_ledger.accounts["Assets"].meta
    assert not example_ledger.accounts["NOACCOUNT"].meta


def test_account_uptodate_status(example_ledger: FavaLedger) -> None:
    func = example_ledger.account_uptodate_status
    assert func("Assets:US:BofA") is None
    assert func("Assets:US:BofA:Checking") == "yellow"
    assert func("Liabilities:US:Chase:Slate") == "green"
