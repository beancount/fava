# pylint: disable=missing-docstring
from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest
from beancount.core.compare import hash_entry
from flask import Flask
from flask import url_for
from flask.testing import FlaskClient
from pytest import MonkeyPatch

from .conftest import SnapshotFunc
from fava.context import g
from fava.core import FavaLedger
from fava.core.misc import align
from fava.json_api import validate_func_arguments
from fava.json_api import ValidationError

if TYPE_CHECKING:
    from werkzeug.test import TestResponse


def test_validate_get_args() -> None:
    def noparams() -> None:
        pass

    assert validate_func_arguments(noparams) is None

    def func(test: str) -> None:
        assert test and isinstance(test, str)

    validator = validate_func_arguments(func)
    assert validator
    with pytest.raises(ValidationError):
        validator({"notest": "value"})
    assert validator({"test": "value"}) == ["value"]


def assert_api_error(response: TestResponse, msg: str | None = None) -> None:
    """Asserts that the response errored and contains the message."""
    assert response.status_code == 200
    assert response.json
    assert not response.json["success"], response.json
    if msg:
        assert msg == response.json["error"]


def assert_api_success(
    response: TestResponse, data: Any | None = None
) -> None:
    """Asserts that the request was successful and contains the data."""
    assert response.status_code == 200
    assert response.json
    assert response.json["success"], response.json
    if data:
        assert data == response.json["data"]


def test_api_changed(app: Flask, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_changed")

    response = test_client.get(url)
    assert_api_success(response, False)


def test_api_add_document(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setitem(
            g.ledger.options, "documents", [str(tmp_path)]  # type: ignore
        )
        request_data = {
            "folder": str(tmp_path),
            "account": "Expenses:Food:Restaurant",
            "file": (BytesIO(b"asdfasdf"), "2015-12-12 test"),
        }
        url = url_for("json_api.put_add_document")

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


def test_api_errors(test_client: FlaskClient) -> None:
    response = test_client.get("/long-example/api/errors")
    assert_api_success(response, 0)


def test_api_context(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
    example_ledger: FavaLedger,
) -> None:
    response = test_client.get("/long-example/api/context")
    assert_api_error(
        response, "Invalid API request: Parameter `entry_hash` is missing."
    )

    entry_hash = hash_entry(
        next(
            entry
            for entry in example_ledger.all_entries
            if entry.meta["lineno"] == 3732
        )
    )
    response = test_client.get(
        f"/long-example/api/context?entry_hash={entry_hash}"
    )
    assert_api_success(response)
    snapshot(response.json)

    entry_hash = hash_entry(example_ledger.entries[10])
    response = test_client.get(
        f"/long-example/api/context?entry_hash={entry_hash}"
    )
    assert_api_success(response)
    assert response.json
    assert not response.json.get("balances_before")
    snapshot(response.json)


def test_api_payee_accounts(test_client: FlaskClient) -> None:
    response = test_client.get("/long-example/api/payee_accounts?payee=test")
    assert_api_success(response, [])


def test_api_move(test_client: FlaskClient) -> None:
    response = test_client.get("/long-example/api/move")
    assert_api_error(
        response, "Invalid API request: Parameter `account` is missing."
    )


def test_api_source_put(
    test_client: FlaskClient, example_ledger: FavaLedger
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
            "file_path": path,
        },
    )
    sha256sum = hashlib.sha256(path.read_bytes()).hexdigest()
    assert_api_success(response, sha256sum)

    # check if the file has been written
    assert path.read_text("utf-8") == "asdf" + payload

    # write original source file
    result = test_client.put(
        url,
        json={"source": payload, "sha256sum": sha256sum, "file_path": path},
    )
    assert result.status_code == 200
    assert path.read_text("utf-8") == payload


def test_api_format_source(
    test_client: FlaskClient, example_ledger: FavaLedger
) -> None:
    path = Path(example_ledger.beancount_file_path)
    url = "/long-example/api/format_source"

    payload = path.read_text("utf-8")

    response = test_client.put(url, json={"source": payload})
    assert_api_success(response, align(payload, 61))


def test_api_format_source_options(
    app: Flask, test_client: FlaskClient, monkeypatch: MonkeyPatch
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        path = Path(g.ledger.beancount_file_path)
        payload = path.read_text("utf-8")

        url = url_for("json_api.put_format_source")

        monkeypatch.setattr(g.ledger.fava_options, "currency_column", 90)

        response = test_client.put(url, json={"source": payload})
        assert_api_success(response, align(payload, 90))


def test_api_add_entries(
    app: Flask,
    test_client: FlaskClient,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
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
                "narration": "Test",
                "meta": {},
                "postings": [
                    {"account": "Assets:US:ETrade:Cash", "amount": "100 USD"},
                    {"account": "Assets:US:ETrade:GLD"},
                ],
            },
        ]

        url = url_for("json_api.put_add_entries")

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
    "query_string,result_str",
    [
        ("balances from year = 2014", "5086.65 USD"),
        ("nononono", "ERROR: Syntax error near"),
        ("select sum(day)", "43558"),
    ],
)
def test_api_query_result(
    query_string: str, result_str: str, test_client: FlaskClient
) -> None:
    response = test_client.get(
        f"/long-example/api/query_result?query_string={query_string}"
    )
    assert response.status_code == 200
    assert result_str in response.get_data(True)


def test_api_query_result_filters(test_client: FlaskClient) -> None:
    response = test_client.get(
        "/long-example/api/query_result?time=2021&query_string=select sum(day)"
    )
    assert response.status_code == 200
    assert "6882" in response.get_data(True)
