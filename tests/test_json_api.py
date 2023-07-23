from __future__ import annotations

import datetime
import hashlib
import re
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.beans.funcs import hash_entry
from fava.context import g
from fava.core.charts import dumps
from fava.core.fava_options import InsertEntryOption
from fava.core.file import get_entry_slice
from fava.core.file import insert_entry
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
    assert_api_success(response, False)


def test_api_add_document(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setitem(g.ledger.options, "documents", [str(tmp_path)])
        request_data = {
            "folder": str(tmp_path),
            "account": "Expenses:Food:Restaurant",
            "file": (BytesIO(b"asdfasdf"), "2015-12-12 test"),
        }
        url = "/long-example/api/add_document"

        response = test_client.put(url)
        assert_api_error(response, "No file uploaded.")

        filename = (
            tmp_path / "Expenses" / "Food" / "Restaurant" / "2015-12-12 test"
        )

        response = test_client.put(url, data=request_data)
        assert_api_success(response, f"Uploaded to {filename}")
        assert Path(filename).is_file()

        request_data["file"] = (BytesIO(b"asdfasdf"), "2015-12-12 test")
        response = test_client.put(url, data=request_data)
        assert_api_error(response, f"{filename} already exists.")


def test_api_upload_import_file(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setattr(
            g.ledger.fava_options,
            "import_dirs",
            [str(tmp_path)],
        )
        request_data = {
            "file": (BytesIO(b"asdfasdf"), "recipt.pdf"),
        }
        url = "/long-example/api/upload_import_file"

        response = test_client.put(url)
        assert_api_error(response, "No file uploaded.")

        filename = tmp_path / "recipt.pdf"

        response = test_client.put(url, data=request_data)
        assert_api_success(response, f"Uploaded to {filename}")
        assert Path(filename).is_file()

        # Uploading the exact same file should fail due to path conflict
        request_data["file"] = (BytesIO(b"asdfasdf"), "recipt.pdf")
        response = test_client.put(url, data=request_data)
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
    snapshot(data)

    entry_hash = hash_entry(example_ledger.all_entries[10])
    response = test_client.get(
        "/long-example/api/context",
        query_string={"entry_hash": entry_hash},
    )
    data = assert_api_success(response)
    snapshot(data)
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
    snapshot(data)


def test_api_payee_transaction(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get(
        "/long-example/api/payee_transaction",
        query_string={"payee": "EDISON POWER"},
    )
    data = assert_api_success(response)
    snapshot(data)


def test_api_imports(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get("/import/api/imports")
    data = assert_api_success(response)
    assert data
    snapshot(data)

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
    snapshot(data)


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


def test_api_source_put(
    test_client: FlaskClient,
    example_ledger: FavaLedger,
) -> None:
    path = Path(example_ledger.beancount_file_path)

    url = "/long-example/api/source"
    # test bad request
    response = test_client.put(url)
    assert_api_error(response, "Invalid JSON request.")

    payload = path.read_text("utf-8")
    sha256sum = hashlib.sha256(path.read_bytes()).hexdigest()

    # change source
    response = test_client.put(
        url,
        json={
            "source": "asdf" + payload,
            "sha256sum": sha256sum,
            "file_path": str(path),
        },
    )
    sha256sum = hashlib.sha256(path.read_bytes()).hexdigest()
    assert_api_success(response, sha256sum)

    # check if the file has been written
    assert path.read_text("utf-8") == "asdf" + payload

    # write original source file
    result = test_client.put(
        url,
        json={
            "source": payload,
            "sha256sum": sha256sum,
            "file_path": str(path),
        },
    )
    assert result.status_code == 200
    assert path.read_text("utf-8") == payload


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


def test_api_source_slice_delete(
    test_client: FlaskClient,
    example_ledger: FavaLedger,
) -> None:
    path = Path(example_ledger.beancount_file_path)
    contents = path.read_text("utf-8")

    url = "/long-example/api/source_slice"
    # test bad request
    response = test_client.delete(url)
    assert_api_error(
        response,
        "Invalid API request: Parameter `entry_hash` is missing.",
    )

    entry = next(
        entry
        for entry in example_ledger.all_entries_by_type.Transaction
        if entry.payee == "Chichipotle"
        and entry.date == datetime.date(2016, 5, 3)
    )
    entry_hash = hash_entry(entry)
    entry_source, sha256sum = get_entry_slice(entry)

    # delete entry
    response = test_client.delete(
        url,
        query_string={
            "entry_hash": entry_hash,
            "sha256sum": sha256sum,
        },
    )
    assert_api_success(response, f"Deleted entry {entry_hash}.")

    assert path.read_text("utf-8") != contents

    insert_option = InsertEntryOption(
        datetime.date(1, 1, 1),
        re.compile(".*"),
        entry.meta["filename"],
        entry.meta["lineno"],
    )
    insert_entry(entry, entry.meta["filename"], [insert_option], 59, 2)
    assert path.read_text("utf-8") == contents


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
                "type": "Transaction",
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
                "type": "Transaction",
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
                "type": "Transaction",
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

        response = test_client.put(url, json={"entries": entries})
        assert_api_success(response, "Stored 3 entries.")

        assert test_file.read_text("utf-8") == """
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


@pytest.mark.parametrize(
    ("query_string", "result_str"),
    [
        ("balances from year = 2014", "5086.65 USD"),
        ("select sum(day)", "43558"),
    ],
)
def test_api_query_result(
    query_string: str,
    result_str: str,
    test_client: FlaskClient,
) -> None:
    response = test_client.get(
        "/long-example/api/query_result",
        query_string={"query_string": query_string},
    )
    data = assert_api_success(response)
    assert result_str in data["table"]


def test_api_query_result_error(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/long-example/api/query_result",
        query_string={"query_string": "nononono"},
    )
    assert response.status_code == 200
    assert "ERROR: Syntax error near" in response.get_data(True)


def test_api_query_result_filters(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/long-example/api/query_result",
        query_string={"query_string": "select sum(day)", "time": "2021"},
    )
    data = assert_api_success(response)
    assert data["chart"] is None
    assert "6882" in data["table"]


def test_api_query_result_charts(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    query_string = (
        "SELECT payee, SUM(COST(position)) AS balance "
        "WHERE account ~ 'Assets' GROUP BY payee, account"
    )
    response = test_client.get(
        "/long-example/api/query_result",
        query_string={"query_string": query_string},
    )
    data = assert_api_success(response)
    assert data["chart"]
    snapshot(data["chart"])


def test_api_commodities(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    response = test_client.get("/long-example/api/commodities")
    data = assert_api_success(response)
    snapshot(data)

    response = test_client.get(
        "/long-example/api/commodities",
        query_string={"time": "3000"},
    )
    data = assert_api_success(response)
    assert not data


def test_api_events(test_client: FlaskClient, snapshot: SnapshotFunc) -> None:
    response = test_client.get("/long-example/api/events")
    data = assert_api_success(response)
    snapshot(dumps(data))
