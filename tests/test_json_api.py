# pylint: disable=missing-docstring
import hashlib
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import Optional

import pytest
from flask import g
from flask import url_for

from fava.core.charts import dumps
from fava.core.misc import align


def assert_api_error(response, msg: Optional[str] = None) -> None:
    """Asserts that the response errored and contains the message."""
    assert response.status_code == 200
    assert not response.json["success"]
    if msg:
        assert msg in response.json["error"]


def assert_api_success(response, data: Optional[Any] = None) -> None:
    """Asserts that the request was successful and contains the data."""
    assert response.status_code == 200
    assert response.json["success"]
    if data:
        assert data == response.json["data"]


def test_api_changed(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.changed")

    response = test_client.get(url)
    assert_api_success(response, False)


def test_api_add_document(app, test_client, tmp_path, monkeypatch) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setitem(g.ledger.options, "documents", [str(tmp_path)])
        request_data = {
            "folder": str(tmp_path),
            "account": "Expenses:Food:Restaurant",
            "file": (BytesIO(b"asdfasdf"), "2015-12-12 test"),
        }
        url = url_for("json_api.add_document")

        response = test_client.put(url)
        assert response.status_code == 400

        filename = (
            tmp_path / "Expenses" / "Food" / "Restaurant" / "2015-12-12 test"
        )

        response = test_client.put(url, data=request_data)
        assert_api_success(response, f"Uploaded to {filename}")
        assert Path(filename).is_file()

        request_data["file"] = (BytesIO(b"asdfasdf"), "2015-12-12 test")
        response = test_client.put(url, data=request_data)
        assert_api_error(response, f"{filename} already exists.")


def test_api_errors(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.errors")

    response = test_client.get(url)
    assert_api_success(response, 0)


def test_api_payee_accounts(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.payee_accounts", payee="test")

    response = test_client.get(url)
    assert_api_success(response, [])


def test_api_move(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.move")

    response = test_client.get(url)
    assert_api_error(response)


def test_api_source_put(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.source")
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
        data=dumps(
            {
                "source": "asdf" + payload,
                "sha256sum": sha256sum,
                "file_path": path,
            }
        ),
        content_type="application/json",
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
        data=dumps(
            {"source": payload, "sha256sum": sha256sum, "file_path": path}
        ),
        content_type="application/json",
    )
    assert result.status_code == 200
    with open(path, encoding="utf-8") as file_handle:
        assert file_handle.read() == payload


def test_api_format_source(app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.format_source")
        path = g.ledger.beancount_file_path

    with open(path, encoding="utf-8") as file_handle:
        payload = file_handle.read()

    response = test_client.put(
        url,
        data=dumps({"source": payload}),
        content_type="application/json",
    )
    assert_api_success(response, align(payload, 61))


def test_api_format_source_options(app, test_client, monkeypatch) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        path = g.ledger.beancount_file_path
        with open(path, encoding="utf-8") as file_handle:
            payload = file_handle.read()

        url = url_for("json_api.format_source")

        monkeypatch.setitem(g.ledger.fava_options, "currency-column", 90)

        response = test_client.put(
            url,
            data=dumps({"source": payload}),
            content_type="application/json",
        )
        assert_api_success(response, align(payload, 90))


def test_api_add_entries(app, test_client, tmp_path, monkeypatch):
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        test_file = tmp_path / "test_file"
        test_file.open("a")
        monkeypatch.setattr(g.ledger, "beancount_file_path", str(test_file))

        data = {
            "entries": [
                {
                    "type": "Transaction",
                    "date": "2017-12-12",
                    "flag": "*",
                    "payee": "Test3",
                    "narration": "",
                    "meta": {},
                    "postings": [
                        {
                            "account": "Assets:US:ETrade:Cash",
                            "amount": "100 USD",
                        },
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
                        {
                            "account": "Assets:US:ETrade:Cash",
                            "amount": "100 USD",
                        },
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
                        {
                            "account": "Assets:US:ETrade:Cash",
                            "amount": "100 USD",
                        },
                        {"account": "Assets:US:ETrade:GLD"},
                    ],
                },
            ]
        }
        url = url_for("json_api.add_entries")

        response = test_client.put(
            url, data=dumps(data), content_type="application/json"
        )
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
def test_api_query_result(query_string, result_str, app, test_client) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        url = url_for("json_api.query_result", query_string=query_string)

    response = test_client.get(url)
    assert response.status_code == 200
    assert result_str in response.get_data(True)
