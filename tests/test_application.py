"""Tests for Fava's main Flask app."""

from __future__ import annotations

import datetime
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from beancount import __version__ as beancount_version

from fava import __version__ as fava_version
from fava.application import create_app
from fava.application import SERVER_SIDE_REPORTS
from fava.application import static_url
from fava.beans import create
from fava.beans.funcs import hash_entry
from fava.context import g
from fava.core import StatementMetadataInvalidError
from fava.core import StatementNotFoundError
from fava.core.group_entries import group_entries_by_type

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse

    from .conftest import SnapshotFunc

FILTER_COMBINATIONS = [
    {"account": "Assets"},
    {"filter": "any(account: Assets)"},
    {"time": "2015", "filter": "#tag1 payee:BayBook"},
]


def assert_success(response: TestResponse) -> str:
    """Asserts that the request was successful and return the data."""
    assert response.status_code == HTTPStatus.OK.value
    return response.get_data(as_text=True)


@pytest.mark.parametrize(
    ("report", "filters"),
    [
        (report, filters)
        for report in SERVER_SIDE_REPORTS
        for filters in FILTER_COMBINATIONS
    ],
)
def test_reports(
    test_client: FlaskClient,
    report: str,
    filters: dict[str, str],
) -> None:
    """The standard reports work without error (content isn't checked here)."""
    response = test_client.get(
        f"/long-example/{report}/", query_string=filters
    )
    assert_success(response)


def test_client_side_reports(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    """The client-side rendered reports are generated."""
    response = test_client.get("/long-example/documents/")
    documents_html = assert_success(response)
    snapshot(documents_html)

    response = test_client.get("/long-example/account/Assets/")
    assert documents_html == assert_success(response)

    response = test_client.get("/long-example/holdings/by_account/")
    assert documents_html == assert_success(response)


def test_redirect(test_client: FlaskClient) -> None:
    """Redirect from root."""
    response = test_client.get("/")
    assert response.status_code == HTTPStatus.FOUND.value
    assert response.location == "/long-example/income_statement/"


@pytest.mark.parametrize(
    ("url"),
    [
        ("/asdfasdf/"),
        ("/asdfasdf/asdfasdf/"),
        ("/example/document/"),
        ("/example/document/?filename=not-path"),
        ("/example/not-a-report/"),
        ("/example/holdings/not-a-holdings-aggregation-key/"),
        ("/example/holdings/by_not-a-holdings-aggregation-key/"),
        ("/example/account/Assets:US:BofA:Checking/not_a_subreport/"),
    ],
)
def test_urls_not_found(test_client: FlaskClient, url: str) -> None:
    """Some URLs return a 404."""
    response = test_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND.value


@pytest.mark.parametrize(
    ("url", "option", "expect"),
    [
        ("/", None, "/long-example/income_statement/"),
        ("/long-example/", None, "/long-example/income_statement/"),
        ("/", "income_statement/", "/long-example/income_statement/"),
        (
            "/long-example/",
            "income_statement/",
            "/long-example/income_statement/",
        ),
        (
            "/",
            "balance_sheet/?account=Assets:US:BofA:Checking",
            "/long-example/balance_sheet/?account=Assets:US:BofA:Checking",
        ),
        (
            "/long-example/",
            "income_statement/?account=Assets:US:BofA:Checking",
            "/long-example/income_statement/?account=Assets:US:BofA:Checking",
        ),
        (
            "/",
            "balance_sheet/?time=year-2+-+year",
            "/long-example/balance_sheet/?time=year-2+-+year",
        ),
        (
            "/",
            "balance_sheet/?time=year-2 - year",
            "/long-example/balance_sheet/?time=year-2%20-%20year",
        ),
        (
            "/",
            "trial_balance/?time=2014&account=Expenses:Rent",
            "/long-example/trial_balance/?time=2014&account=Expenses:Rent",
        ),
    ],
)
def test_default_path_redirection(
    app: Flask,
    test_client: FlaskClient,
    url: str,
    option: str | None,
    expect: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that default-page option redirects as expected."""
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        if option:
            monkeypatch.setattr(g.ledger.fava_options, "default_page", option)
        response = test_client.get(url)
        get_url = response.headers.get("Location", "")
        assert response.status_code == HTTPStatus.FOUND.value
        assert get_url == expect


@pytest.mark.parametrize(
    ("referer", "jump_link", "expect"),
    [
        ("/?foo=bar", "/jump?foo=baz", "/?foo=baz"),
        ("/?foo=bar", "/jump?baz=qux", "/?foo=bar&baz=qux"),
        ("/", "/jump?foo=bar&baz=qux", "/?foo=bar&baz=qux"),
        ("/", "/jump?baz=qux", "/?baz=qux"),
        ("/?foo=bar", "/jump?foo=", "/"),
        ("/?foo=bar", "/jump?foo=&foo=", "/?foo=&foo="),
        ("/", "/jump?foo=", "/"),
    ],
)
def test_jump_handler(
    test_client: FlaskClient,
    referer: str,
    jump_link: str,
    expect: str,
) -> None:
    """Test /jump handler correctly redirect to the right location.

    Note: according to RFC 2616, Location: header should use an absolute URL.
    """
    response = test_client.get(jump_link, headers=[("Referer", referer)])
    get_url = response.headers.get("Location", "")
    assert response.status_code == HTTPStatus.FOUND.value
    assert get_url == expect


def test_help_pages(test_client: FlaskClient) -> None:
    """Help pages."""
    response = test_client.get("/long-example/help/")
    help_page = assert_success(response)
    assert f"Fava <code>{fava_version}</code>" in help_page
    assert f"<code>{beancount_version}</code>" in help_page
    response = test_client.get("/long-example/help/filters")
    assert assert_success(response)
    response = test_client.get("/long-example/help/asdfasdf")
    assert response.status_code == HTTPStatus.NOT_FOUND.value


def test_query_download(test_client: FlaskClient) -> None:
    """Download query as csv."""
    result = test_client.get(
        "/long-example/download-query/query_result.csv",
        query_string={"query_string": "balances"},
    )
    assert_success(result)


def test_statement_download(
    app: Flask, test_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Download entry statement."""

    path = Path(__file__)
    by_account = path.parent.parent / "found_by_account"
    date = datetime.date(2022, 1, 1)
    txn = create.transaction(
        {
            "filename": str(path),
            "lineno": 1,
            "statement": path.name,
            "account-statement": "found_by_account",
            "missing-statement": "asdf",
        },
        date,
        "*",
        "payee",
        "narration",
        postings=[create.posting("Assets:Cash", create.amount("10 EUR"))],
    )
    txn_hash = hash_entry(txn)
    entries = [
        create.document({}, date, "Assets:Cash", str(by_account)),
        create.document({}, date, "Assets", str(path)),
        txn,
    ]

    with app.test_request_context("/long-example/"):
        app.preprocess_request()

        monkeypatch.setattr(g.ledger, "all_entries", entries)
        monkeypatch.setattr(
            g.ledger, "all_entries_by_type", group_entries_by_type(entries)
        )
        assert g.ledger.get_entry(txn_hash) == txn
        with pytest.raises(StatementMetadataInvalidError):
            g.ledger.statement_path(txn_hash, "asdf")
        with pytest.raises(StatementMetadataInvalidError):
            g.ledger.statement_path(txn_hash, "lineno")
        with pytest.raises(StatementNotFoundError):
            g.ledger.statement_path(txn_hash, "missing-statement")
        assert Path(g.ledger.statement_path(txn_hash, "statement")) == path
        assert (
            Path(g.ledger.statement_path(txn_hash, "account-statement"))
            == by_account
        )

        response = test_client.get(
            "/long-example/statement/",
            query_string={"entry_hash": txn_hash, "key": "statement"},
        )
        assert_success(response)

        response = test_client.get(
            "/long-example/statement/",
            query_string={"entry_hash": "asdf", "key": "asdf"},
        )
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_incognito(test_data_dir: Path) -> None:
    """Numbers get obfuscated in incognito mode."""
    app = create_app([test_data_dir / "example.beancount"], incognito=True)
    test_client = app.test_client()
    response = test_client.get("/example/journal/")
    assert "XXX" in assert_success(response)

    response = test_client.get("/example/api/commodities")
    assert "XXX" not in assert_success(response)


def test_read_only_mode(test_data_dir: Path) -> None:
    """Non GET requests returns 401 in read-only mode"""
    app = create_app([test_data_dir / "example.beancount"], read_only=True)
    test_client = app.test_client()

    response = test_client.get("/")
    assert response.status_code == HTTPStatus.FOUND.value

    for method in [
        test_client.delete,
        test_client.patch,
        test_client.post,
        test_client.put,
    ]:
        response = method("/any/path/")
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value


def test_download_journal(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    """The currently filtered journal can be downloaded."""
    response = test_client.get(
        "/long-example/download-journal/",
        query_string={"time": "2016-05-07"},
    )
    snapshot(response.get_data(as_text=True))
    assert response.headers["Content-Disposition"].startswith(
        'attachment; filename="journal_',
    )
    assert response.headers["Content-Type"] == "application/octet-stream"


def test_static_url(app: Flask) -> None:
    """Static URLs have the mtime appended."""
    with app.test_request_context():
        url = static_url("app.js")
        assert url.startswith("/static/app.js?mtime=")
        url = static_url("nonexistent.js")
        assert url == "/static/nonexistent.js?mtime=0"


def test_load_extension_reports(test_client: FlaskClient) -> None:
    """Extension can register reports."""

    url = "/extension-report/extension/FavaExtTest/"
    response = test_client.get(url)
    assert_success(response)
    url = "/extension-report/extension_js_module/FavaExtTest.js"
    response = test_client.get(url)
    assert_success(response)


@pytest.mark.parametrize(
    ("url"),
    [
        ("/extension-report/extension/MissingExtension/"),
        ("/extension-report/extension/MissingExtension/example_data"),
        ("/extension-report/extension_js_module/Missing.js"),
        ("/extension-report/extension/FavaExtTest/missing_endpoint"),
    ],
)
def test_load_extension_not_found(test_client: FlaskClient, url: str) -> None:
    response = test_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND.value


def test_load_extension_endpoint(test_client: FlaskClient) -> None:
    url = "/extension-report/extension/FavaExtTest/example_data"
    response = test_client.get(url)
    assert assert_success(response)
    assert response.json == ["some data"]
