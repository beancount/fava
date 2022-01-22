# pylint: disable=missing-docstring
from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from beancount.core.compare import hash_entry
from flask import url_for
from flask.testing import FlaskClient

from fava.context import g
from fava.core import FavaLedger
from fava.core.misc import align
from fava.json_api import validate_func_arguments
from fava.json_api import ValidationError


def test_validate_get_args() -> None:
    def func(test: str):
        assert test and isinstance(test, str)

    validator = validate_func_arguments(func)
    with pytest.raises(ValidationError):
        validator({"notest": "value"})
    assert validator({"test": "value"}) == ["value"]


def assert_api_error(response, msg: str | None = None) -> None:
    """Asserts that the response errored and contains the message."""
    assert response.status_code == 200
    assert not response.json["success"], response.json
    if msg:
        assert msg == response.json["error"]


def assert_api_success(response, data: Any | None = None) -> None:
    """Asserts that the request was successful and contains the data."""
    assert response.status_code == 200
    assert response.json["success"], response.json
    if data:
        assert data == response.json["data"]


def test_api_changed(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_changed")

    response = test_client.get(url)
    assert_api_success(response, False)


def test_api_add_document(
    app, test_client: FlaskClient, tmp_path: Path, monkeypatch
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setitem(g.ledger.options, "documents", [str(tmp_path)])
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


def test_api_errors(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_errors")

    response = test_client.get(url)
    assert_api_success(response, 0)


def test_api_context(
    app, test_client: FlaskClient, snapshot, example_ledger: FavaLedger
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        url = url_for("json_api.get_context")
        response = test_client.get(url)
        assert_api_error(
            response, "Invalid API request: Parameter `entry_hash` is missing."
        )

        url = url_for(
            "json_api.get_context",
            entry_hash=hash_entry(
                next(
                    entry
                    for entry in example_ledger.all_entries
                    if entry.meta["lineno"] == 3732
                )
            ),
        )
        response = test_client.get(url)
        assert_api_success(response)
        snapshot(response.json)

        url = url_for(
            "json_api.get_context",
            entry_hash=hash_entry(example_ledger.entries[10]),
        )
        response = test_client.get(url)
        assert_api_success(response)
        assert not response.json.get("balances_before")
        snapshot(response.json)


def test_api_payee_accounts(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_payee_accounts", payee="test")

    response = test_client.get(url)
    assert_api_success(response, [])


def test_api_move(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_move")

    response = test_client.get(url)
    assert_api_error(
        response, "Invalid API request: Parameter `account` is missing."
    )


def test_api_source_put(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.put_source")
        path = g.ledger.beancount_file_path

    # test bad request
    response = test_client.put(url)
    assert_api_error(response, "Invalid JSON request.")

    with open(path, encoding="utf-8") as file_handle:
        payload = file_handle.read()
    with open(path, mode="rb") as bfile_handle:
        sha256sum = hashlib.sha256(bfile_handle.read()).hexdigest()

    # change source
    response = test_client.put(
        url,
        json={
            "source": "asdf" + payload,
            "sha256sum": sha256sum,
            "file_path": path,
        },
    )
    with open(path, mode="rb") as bfile_handle:
        sha256sum = hashlib.sha256(bfile_handle.read()).hexdigest()
    assert_api_success(response, sha256sum)

    # check if the file has been written
    with open(path, encoding="utf-8") as file_handle:
        assert file_handle.read() == "asdf" + payload

    # write original source file
    result = test_client.put(
        url,
        json={"source": payload, "sha256sum": sha256sum, "file_path": path},
    )
    assert result.status_code == 200
    with open(path, encoding="utf-8") as file_handle:
        assert file_handle.read() == payload


def test_api_format_source(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.put_format_source")
        path = g.ledger.beancount_file_path

    with open(path, encoding="utf-8") as file_handle:
        payload = file_handle.read()

    response = test_client.put(url, json={"source": payload})
    assert_api_success(response, align(payload, 61))


def test_api_format_source_options(
    app, test_client: FlaskClient, monkeypatch
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        path = g.ledger.beancount_file_path
        with open(path, encoding="utf-8") as file_handle:
            payload = file_handle.read()

        url = url_for("json_api.put_format_source")

        monkeypatch.setattr(g.ledger.fava_options, "currency_column", 90)

        response = test_client.put(url, json={"source": payload})
        assert_api_success(response, align(payload, 90))


def test_api_add_entries(
    app, test_client: FlaskClient, tmp_path: Path, monkeypatch
):
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
    query_string, result_str, app, test_client: FlaskClient
) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.get_query_result", query_string=query_string)

    response = test_client.get(url)
    assert response.status_code == 200
    assert result_str in response.get_data(True)


def test_api_query_result_filters(app, test_client: FlaskClient) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for(
            "json_api.get_query_result",
            query_string="select sum(day)",
            time="2021",
        )

    response = test_client.get(url)
    assert response.status_code == 200
    assert "6882" in response.get_data(True)
