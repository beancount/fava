# pylint: disable=missing-docstring


import hashlib
from io import BytesIO
import os

import flask
import pytest

from fava.core.misc import align


def test_api_changed(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for("json_api.changed")

    result = test_client.get(url)
    response_data = flask.json.loads(result.get_data(True))
    assert response_data == {"data": False, "success": True}


def test_api_add_document(app, test_client, tmpdir):
    with app.test_request_context():
        app.preprocess_request()
        old_documents = flask.g.ledger.options["documents"]
        flask.g.ledger.options["documents"] = [str(tmpdir)]
        request_data = {
            "folder": str(tmpdir),
            "account": "Expenses:Food:Restaurant",
            "file": (BytesIO(b"asdfasdf"), "2015-12-12 test"),
        }
        url = flask.url_for("json_api.add_document")

        response = test_client.put(url)
        assert response.status_code == 400

        filename = os.path.join(
            str(tmpdir), "Expenses", "Food", "Restaurant", "2015-12-12 test"
        )

        response = test_client.put(url, data=request_data)
        print(flask.json.loads(response.get_data(True)))
        assert flask.json.loads(response.get_data(True)) == {
            "success": True,
            "data": "Uploaded to {}".format(filename),
        }
        assert os.path.isfile(filename)

        request_data["file"] = (BytesIO(b"asdfasdf"), "2015-12-12 test")
        response = test_client.put(url, data=request_data)
        assert flask.json.loads(response.get_data(True)) == {
            "success": False,
            "error": "{} already exists.".format(filename),
        }
        flask.g.ledger.options["documents"] = old_documents


def test_api_source_put(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for("json_api.source")

    # test bad request
    response = test_client.put(url)
    response_data = flask.json.loads(response.get_data(True))
    assert response_data == {
        "error": "Invalid JSON request.",
        "success": False,
    }
    assert response.status_code == 200

    path = app.config["BEANCOUNT_FILES"][0]
    payload = open(path, encoding="utf-8").read()
    sha256sum = hashlib.sha256(open(path, mode="rb").read()).hexdigest()

    # change source
    result = test_client.put(
        url,
        data=flask.json.dumps(
            {
                "source": "asdf" + payload,
                "sha256sum": sha256sum,
                "file_path": path,
            }
        ),
        content_type="application/json",
    )
    assert result.status_code == 200
    response_data = flask.json.loads(result.get_data(True))
    sha256sum = hashlib.sha256(open(path, mode="rb").read()).hexdigest()
    assert response_data == {"success": True, "data": sha256sum}

    # check if the file has been written
    assert open(path, encoding="utf-8").read() == "asdf" + payload

    # write original source file
    result = test_client.put(
        url,
        data=flask.json.dumps(
            {"source": payload, "sha256sum": sha256sum, "file_path": path}
        ),
        content_type="application/json",
    )
    assert result.status_code == 200
    assert open(path, encoding="utf-8").read() == payload


def test_api_format_source(app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for("json_api.format_source")

    path = app.config["BEANCOUNT_FILES"][0]
    payload = open(path, encoding="utf-8").read()

    result = test_client.put(
        url,
        data=flask.json.dumps({"source": payload}),
        content_type="application/json",
    )
    data = flask.json.loads(result.get_data(True))
    assert data == {"data": align(payload, {}), "success": True}


def test_api_format_source_options(app, test_client):
    # pylint: disable=too-many-function-args
    path = app.config["BEANCOUNT_FILES"][0]
    payload = open(path, encoding="utf-8").read()
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for("json_api.format_source")
        old_currency_column = flask.g.ledger.fava_options["currency-column"]
        flask.g.ledger.fava_options["currency-column"] = 90

        result = test_client.put(
            url,
            data=flask.json.dumps({"source": payload}),
            content_type="application/json",
        )
        data = flask.json.loads(result.get_data(True))
        assert data == {
            "data": align(payload, {"currency-column": 90}),
            "success": True,
        }

        flask.g.ledger.fava_options["currency-column"] = old_currency_column


def test_api_add_entries(app, test_client, tmpdir):
    with app.test_request_context():
        app.preprocess_request()
        old_beancount_file = flask.g.ledger.beancount_file_path
        test_file = tmpdir.join("test_file")
        test_file.open("a")
        flask.g.ledger.beancount_file_path = str(test_file)

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
        url = flask.url_for("json_api.add_entries")

        response = test_client.put(
            url, data=flask.json.dumps(data), content_type="application/json"
        )
        assert flask.json.loads(response.get_data(True)) == {
            "success": True,
            "data": "Stored 3 entries.",
        }

        assert (
            test_file.read_text("utf-8")
            == """2017-01-12 * "Test1" ""
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

        flask.g.ledger.beancount_file_path = old_beancount_file


@pytest.mark.parametrize(
    "query_string,result_str",
    [
        ("balances from year = 2014", "5086.65 USD"),
        ("nononono", "ERROR: Syntax error near"),
        ("select sum(day)", "43558"),
    ],
)
def test_api_query_result(query_string, result_str, app, test_client):
    with app.test_request_context():
        app.preprocess_request()
        url = flask.url_for("json_api.query_result", query_string=query_string)

    result = test_client.get(url)
    assert result.status_code == 200
    assert result_str in result.get_data(True)
