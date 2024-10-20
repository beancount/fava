from __future__ import annotations

import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.beans.funcs import hash_entry
from fava.context import g
from fava.core.file import _sha256_str
from fava.core.file import get_entry_slice
from fava.core.misc import align
from fava.json_api import validate_func_arguments
from fava.json_api import ValidationError

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse

    from fava.core import FavaLedger

    from .conftest import SnapshotFunc


def test_validate_get_args() -> None:
    def noparams() -> None:
        pass

    assert validate_func_arguments(noparams) is None

    def func(test: str) -> None:
        assert test
        assert isinstance(test, str)

    validator = validate_func_arguments(func)
    assert validator
    with pytest.raises(ValidationError):
        validator({"notest": "value"})
    assert validator({"test": "value"}) == ["value"]


def assert_api_error(response: TestResponse, msg: str | None = None) -> str:
    """Asserts that the response errored and contains the message."""
    assert response.status_code == 200
    assert response.json
    assert not response.json["success"], response.json
    err_msg = response.json["error"]
    assert isinstance(err_msg, str)
    if msg:
        assert msg == err_msg
    return err_msg


def assert_api_success(response: TestResponse, data: Any | None = None) -> Any:
    """Asserts that the request was successful and contains the data."""
    assert response.status_code == 200
    assert response.json
    assert response.json["success"], response.json
    if data is not None:
        assert data == response.json["data"]
    return response.json["data"]


def test_api_changed(test_client: FlaskClient) -> None:
    response = test_client.get("/long-example/api/changed")
    assert_api_success(response, data=False)


def test_api_add_document_and_move_and_delete(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    add_url = "/long-example/api/add_document"
    get_url = "/long-example/document/"
    move_url = "/long-example/api/move"
    delete_url = "/long-example/api/document"
    account = "Expenses:Food:Restaurant"
    account_dir = tmp_path / "Expenses" / "Food" / "Restaurant"

    def _data(
        filename: str,
    ) -> dict[str, str | tuple[BytesIO, str]]:
        return {
            "folder": str(tmp_path),
            "account": account,
            "file": (BytesIO(b"asdfasdf"), filename),
        }

    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        # error when no documents dir is set
        monkeypatch.setitem(g.ledger.options, "documents", [])

        response = test_client.put(add_url)
        assert_api_error(response, "You need to set a documents folder.")

        # upload to temporary directory
        monkeypatch.setitem(g.ledger.options, "documents", [str(tmp_path)])
        monkeypatch.setattr(
            g.ledger.fava_options, "import_dirs", [str(account_dir)]
        )

        response = test_client.put(add_url)
        assert_api_error(response, "No file uploaded.")

        response = test_client.put(add_url, data=_data(""))
        assert_api_error(response, "Uploaded file is missing filename.")

        filename = account_dir / "2015-12-12 test"
        assert not filename.exists()
        response = test_client.put(add_url, data=_data("2015-12-12 test"))
        assert_api_success(response, f"Uploaded to {filename}")
        assert filename.read_text() == "asdfasdf"
        assert filename.is_file()

        response = test_client.get(
            get_url, query_string={"filename": str(filename)}
        )
        assert response.status_code == 200
        assert response.get_data() == b"asdfasdf"

        response = test_client.put(add_url, data=_data("2015-12-12 test"))
        assert_api_error(response, f"{filename} already exists.")

        # move to same path should fail
        response = test_client.get(
            move_url,
            query_string={
                "account": account,
                "filename": str(filename),
                "new_name": "2015-12-12 test",
            },
        )
        assert_api_error(response, f"{filename} already exists.")

        response = test_client.get(
            move_url,
            query_string={
                "account": account,
                "filename": str(filename),
                "new_name": "2015-12-12 test_moved",
            },
        )
        new_filename = account_dir / "2015-12-12 test_moved"
        assert_api_success(response, f"Moved {filename} to {new_filename}.")
        assert not filename.exists()
        assert new_filename.exists()

        # delete
        invalid_filename = tmp_path / "asdf"
        response = test_client.delete(
            delete_url,
            query_string={"filename": str(invalid_filename)},
        )
        assert_api_error(
            response,
            f"Not valid document or import file: '{invalid_filename}'.",
        )

        response = test_client.delete(
            delete_url,
            query_string={"filename": str(filename)},
        )
        assert_api_error(response, f"{filename} does not exist.")

        response = test_client.delete(
            delete_url,
            query_string={"filename": str(new_filename)},
        )
        assert_api_success(response, f"Deleted {new_filename}.")


def test_api_upload_import_file(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = "/long-example/api/upload_import_file"

    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setattr(
            g.ledger.fava_options, "import_dirs", [str(tmp_path)]
        )

        response = test_client.put(url)
        assert_api_error(response, "No file uploaded.")

        response = test_client.put(
            url, data={"file": (BytesIO(b"asdfasdf"), "")}
        )
        assert_api_error(response, "Uploaded file is missing filename.")

        filename = tmp_path / "receipt.pdf"
        assert not filename.is_file()
        response = test_client.put(
            url, data={"file": (BytesIO(b"asdfasdf"), "receipt.pdf")}
        )
        assert_api_success(response, f"Uploaded to {filename}")
        assert filename.is_file()

        # Uploading the exact same file should fail due to path conflict
        response = test_client.put(
            url, data={"file": (BytesIO(b"asdfasdf"), "receipt.pdf")}
        )
        assert_api_error(response, f"{filename} already exists.")


def test_api_errors(test_client: FlaskClient, snapshot: SnapshotFunc) -> None:
    response = test_client.get("/long-example/api/errors")
    assert_api_success(response, [])
    response = test_client.get("/errors/api/errors")
    data = assert_api_success(response)

    def get_message(err: Any) -> str:
        return str(err["message"])

    snapshot(sorted(data, key=get_message))


def test_api_context(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
    example_ledger: FavaLedger,
) -> None:
    response = test_client.get("/long-example/api/context")
    assert_api_error(
        response,
        "Invalid API request: Parameter `entry_hash` is missing.",
    )

    entry_hash = hash_entry(
        next(
            entry
            for entry in example_ledger.all_entries_by_type.Transaction
            if entry.narration == r"Investing 40% of cash in VBMPX"
            and entry.date == datetime.date(2016, 5, 9)
        ),
    )
    response = test_client.get(
        "/long-example/api/context",
        query_string={"entry_hash": entry_hash},
    )
    data = assert_api_success(response)
    snapshot(data, json=True)

    entry_hash = hash_entry(example_ledger.all_entries[10])
    response = test_client.get(
        "/long-example/api/context",
        query_string={"entry_hash": entry_hash},
    )
    data = assert_api_success(response)
    snapshot(data, json=True)
    assert not data.get("balances_before")


def test_api_payee_accounts(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    assert_api_error(test_client.get("/long-example/api/payee_accounts"))

    response = test_client.get(
        "/long-example/api/payee_accounts",
        query_string={"payee": "EDISON POWER"},
    )
    data = assert_api_success(response)
    assert data[0] == "Assets:US:BofA:Checking"
    assert data[1] == "Expenses:Home:Electricity"
    snapshot(data, json=True)


def test_api_payee_transaction(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get(
        "/long-example/api/payee_transaction",
        query_string={"payee": "EDISON POWER"},
    )
    data = assert_api_success(response)
    snapshot(data, json=True)


def test_api_imports(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get("/import/api/imports")
    data = assert_api_success(response)
    assert data
    snapshot(data, json=True)

    importable = next(f for f in data if f["importers"])
    assert importable

    response = test_client.get(
        "/import/api/extract",
        query_string={
            "filename": importable["name"],
            "importer": importable["importers"][0]["importer_name"],
        },
    )
    data = assert_api_success(response)
    snapshot(data, json=True)


def test_api_move(test_client: FlaskClient) -> None:
    response = test_client.get("/long-example/api/move")
    assert_api_error(
        response,
        "Invalid API request: Parameter `account` is missing.",
    )

    invalid = {"account": "Assets", "new_name": "new", "filename": "old"}
    response = test_client.get("/long-example/api/move", query_string=invalid)
    assert_api_error(response, "You need to set a documents folder.")

    response = test_client.get("/import/api/move", query_string=invalid)
    assert_api_error(response, "Not a valid account: 'Assets'")

    response = test_client.get(
        "/import/api/move",
        query_string={
            **invalid,
            "account": "Assets:Checking",
        },
    )
    assert_api_error(response, "Not a file: 'old'")


def test_api_get_source_invalid_unicode(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/invalid-unicode/api/source",
        query_string={"filename": ""},
    )
    err_msg = assert_api_error(response)
    assert "The source file contains invalid unicode" in err_msg


def test_api_get_source_unknown_file(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/example/api/source",
        query_string={"filename": "/home/not-one-of-the-includes"},
    )
    err_msg = assert_api_error(response)
    assert "Trying to read a non-source file" in err_msg


def test_api_source_put(app_in_tmp_dir: Flask) -> None:
    test_client = app_in_tmp_dir.test_client()
    ledger = app_in_tmp_dir.config["LEDGERS"]["edit-example"]
    path = Path(ledger.beancount_file_path)

    url = "/edit-example/api/source"
    # test bad request
    response = test_client.put(url)
    assert_api_error(response, "Invalid JSON request.")

    source = path.read_text("utf-8")
    changed_source = source + "\n;comment"
    sha256sum = _sha256_str(source)

    # change source
    response = test_client.put(
        url,
        json={
            "source": changed_source,
            "sha256sum": sha256sum,
            "file_path": str(path),
        },
    )
    sha256sum = _sha256_str(changed_source)
    assert_api_success(response, sha256sum)

    # check if the file has been written
    assert path.read_text("utf-8") == changed_source

    # write original source file
    result = test_client.put(
        url,
        json={
            "source": source,
            "sha256sum": sha256sum,
            "file_path": str(path),
        },
    )
    assert result.status_code == 200
    assert path.read_text("utf-8") == source


def test_api_format_source(
    test_client: FlaskClient,
    example_ledger: FavaLedger,
) -> None:
    path = Path(example_ledger.beancount_file_path)
    url = "/long-example/api/format_source"

    payload = path.read_text("utf-8")

    response = test_client.put(url, json={"source": payload})
    assert_api_success(response, align(payload, 61))


def test_api_format_source_options(
    app: Flask,
    test_client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        path = Path(g.ledger.beancount_file_path)
        payload = path.read_text("utf-8")

        monkeypatch.setattr(g.ledger.fava_options, "currency_column", 90)

        response = test_client.put(
            "/long-example/api/format_source",
            json={"source": payload},
        )
        assert_api_success(response, align(payload, 90))


def test_api_source_slice_delete(app_in_tmp_dir: Flask) -> None:
    test_client = app_in_tmp_dir.test_client()
    ledger = app_in_tmp_dir.config["LEDGERS"]["edit-example"]
    path = Path(ledger.beancount_file_path)

    contents = path.read_text("utf-8")
    assert '2016-05-03 * "Chichipotle" "Eating out with Joe"' in contents

    url = "/edit-example/api/source_slice"
    # test bad request
    response = test_client.delete(url)
    assert_api_error(
        response,
        "Invalid API request: Parameter `entry_hash` is missing.",
    )

    entry = ledger.all_entries[-1]
    entry_hash = hash_entry(entry)
    _entry_source, sha256sum = get_entry_slice(entry)

    # delete entry
    response = test_client.delete(
        url,
        query_string={"entry_hash": entry_hash, "sha256sum": sha256sum},
    )
    assert_api_success(response, f"Deleted entry {entry_hash}.")
    assert (
        '2016-05-03 * "Chichipotle" "Eating out with Joe"'
        not in path.read_text("utf-8")
    )


def test_api_add_entries(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        test_file = tmp_path / "test_file"
        test_file.open("a")
        monkeypatch.setattr(g.ledger, "beancount_file_path", str(test_file))

        entries = [
            {
                "t": "Transaction",
                "date": "2017-12-12",
                "flag": "*",
                "payee": "Test3",
                "tags": [],
                "links": [],
                "narration": "",
                "meta": {},
                "postings": [
                    {"account": "Assets:US:ETrade:Cash", "amount": "100 USD"},
                    {"account": "Assets:US:ETrade:GLD"},
                ],
            },
            {
                "t": "Transaction",
                "date": "2017-01-12",
                "flag": "*",
                "payee": "Test1",
                "tags": [],
                "links": [],
                "narration": "",
                "meta": {},
                "postings": [
                    {"account": "Assets:US:ETrade:Cash", "amount": "100 USD"},
                    {"account": "Assets:US:ETrade:GLD"},
                ],
            },
            {
                "t": "Transaction",
                "date": "2017-02-12",
                "flag": "*",
                "payee": "Test",
                "tags": [],
                "links": [],
                "narration": "Test",
                "meta": {},
                "postings": [
                    {"account": "Assets:US:ETrade:Cash", "amount": "100 USD"},
                    {"account": "Assets:US:ETrade:GLD"},
                ],
            },
        ]

        url = "/long-example/api/add_entries"

        err = test_client.put(url, json={"entries": "string"})
        assert_api_error(
            err,
            "Invalid API request: Parameter `entries`"
            " of incorrect type - expected <class 'list'>.",
        )

        response = test_client.put(url, json={"entries": entries})
        assert_api_success(response, "Stored 3 entries.")

        assert (
            test_file.read_text("utf-8")
            == """
2017-01-12 * "Test1" ""
  Assets:US:ETrade:Cash                                 100 USD
  Assets:US:ETrade:GLD

2017-02-12 * "Test" "Test"
  Assets:US:ETrade:Cash                                 100 USD
  Assets:US:ETrade:GLD

2017-12-12 * "Test3" ""
  Assets:US:ETrade:Cash                                 100 USD
  Assets:US:ETrade:GLD
"""
        )


@pytest.mark.parametrize(
    ("query_string"),
    [
        ("balances from year = 2014"),
        ("select sum(day)"),
        ("journal from year = 2014 and month = 1"),
        (
            "select day, position, units(position), balance, payee, tags"
            " from year = 2014 and month = 1"
        ),
        ("help"),
    ],
)
def test_api_query_result(
    query_string: str,
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get(
        "/long-example/api/query",
        query_string={"query_string": query_string},
    )
    data = assert_api_success(response)
    snapshot(data, json=True)


def test_api_query_result_error(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/long-example/api/query",
        query_string={"query_string": "nononono"},
    )
    assert response.status_code == 200
    assert "ERROR: Syntax error near" in response.get_data(as_text=True)


def test_api_commodities_empty(
    test_client: FlaskClient,
) -> None:
    response = test_client.get(
        "/long-example/api/commodities?time=3000",
    )
    data = assert_api_success(response)
    assert not data


@pytest.mark.parametrize(
    ("name", "url"),
    [
        ("commodities", "/long-example/api/commodities"),
        ("documents", "/example/api/documents"),
        ("events", "/long-example/api/events"),
        ("income_statement", "/long-example/api/income_statement?time=2014"),
        ("trial_balance", "/long-example/api/trial_balance?time=2014"),
        ("balance_sheet", "/long-example/api/balance_sheet"),
        (
            "balance_sheet_with_cost",
            "/long-example/api/balance_sheet?conversion=at_value",
        ),
        (
            "account_report_off_by_one_journal",
            (
                "/off-by-one/api/account_report"
                "?interval=day&conversion=at_value&a=Assets"
            ),
        ),
        (
            "account_report_off_by_one",
            (
                "/off-by-one/api/account_report"
                "?interval=day&conversion=at_value&a=Assets&r=balances"
            ),
        ),
    ],
)
def test_api(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
    name: str,
    url: str,
) -> None:
    response = test_client.get(url)
    data = assert_api_success(response)
    assert data
    snapshot(data, name=name, json=True)
