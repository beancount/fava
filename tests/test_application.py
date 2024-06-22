"""Tests for Fava's main Flask app."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

import pytest
from beancount import __version__ as beancount_version

from fava import __version__ as fava_version
from fava.application import create_app
from fava.application import SERVER_SIDE_REPORTS
from fava.application import static_url
from fava.context import g

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from flask import Flask
    from flask.testing import FlaskClient

    from .conftest import SnapshotFunc

FILTER_COMBINATIONS = [
    {"account": "Assets"},
    {"filter": "any(account: Assets)"},
    {"time": "2015", "filter": "#tag1 payee:BayBook"},
]


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
    result = test_client.get(f"/long-example/{report}/", query_string=filters)
    assert result.status_code == 200


def test_client_side_reports(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    """The client-side rendered reports are generated."""
    result = test_client.get("/long-example/documents/")
    assert result.status_code == 200
    snapshot(result.get_data(as_text=True))


@pytest.mark.parametrize(
    ("url", "return_code"),
    [
        ("/", 302),
        ("/asdfasdf/", 404),
        ("/asdfasdf/asdfasdf/", 404),
        ("/example/not-a-report/", 404),
        ("/example/holdings/not-a-holdings-aggregation-key/", 404),
        ("/example/holdings/by_not-a-holdings-aggregation-key/", 404),
        ("/example/account/Assets:US:BofA:Checking/not_a_subreport/", 404),
    ],
)
def test_urls(test_client: FlaskClient, url: str, return_code: int) -> None:
    """Some URLs return a 404."""
    result = test_client.get(url)
    assert result.status_code == return_code


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
        result = test_client.get(url)
        get_url = result.headers.get("Location", "")
        # pre Werkzeug 2.1:
        expect_url = urljoin("http://localhost/", expect)
        assert result.status_code == 302
        assert get_url in {expect, expect_url}


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
    app: Flask,
    test_client: FlaskClient,
    referer: str,
    jump_link: str,
    expect: str,
) -> None:
    """Test /jump handler correctly redirect to the right location.

    Note: according to RFC 2616, Location: header should use an absolute URL.
    """
    result = test_client.get(jump_link, headers=[("Referer", referer)])
    with app.test_request_context():
        get_url = result.headers.get("Location", "")
        # pre Werkzeug 2.1:
        expect_url = urljoin("http://localhost/", expect)
        assert result.status_code == 302
        assert get_url in {expect, expect_url}


def test_help_pages(test_client: FlaskClient) -> None:
    """Help pages."""
    result = test_client.get("/long-example/help/")
    assert result.status_code == 200
    assert f"Fava <code>{fava_version}</code>" in result.get_data(as_text=True)
    assert f"<code>{beancount_version}</code>" in result.get_data(as_text=True)
    result = test_client.get("/long-example/help/filters")
    assert result.status_code == 200
    result = test_client.get("/long-example/help/asdfasdf")
    assert result.status_code == 404


def test_query_download(test_client: FlaskClient) -> None:
    """Download query as csv."""
    result = test_client.get(
        "/long-example/download-query/query_result.csv?query_string=balances",
    )
    assert result.status_code == 200


def test_incognito(test_data_dir: Path) -> None:
    """Numbers get obfuscated in incognito mode."""
    app = create_app([test_data_dir / "example.beancount"], incognito=True)
    test_client = app.test_client()
    result = test_client.get("/example/journal/")
    assert result.status_code == 200
    assert "XXX" in result.get_data(as_text=True)

    result = test_client.get("/example/api/commodities")
    assert result.status_code == 200
    assert "XXX" not in result.get_data(as_text=True)


def test_read_only_mode(test_data_dir: Path) -> None:
    """Non GET requests returns 401 in read-only mode"""
    app = create_app([test_data_dir / "example.beancount"], read_only=True)
    test_client = app.test_client()

    assert test_client.get("/").status_code == 302

    for method in [
        test_client.delete,
        test_client.patch,
        test_client.post,
        test_client.put,
    ]:
        result = method("/any/path/")
        assert result.status_code == 401


def test_download_journal(
    test_client: FlaskClient,
    snapshot: SnapshotFunc,
) -> None:
    """The currently filtered journal can be downloaded."""
    result = test_client.get(
        "/long-example/download-journal/",
        query_string={"time": "2016-05-07"},
    )
    snapshot(result.get_data(as_text=True))
    assert result.headers["Content-Disposition"].startswith(
        'attachment; filename="journal_',
    )
    assert result.headers["Content-Type"] == "application/octet-stream"


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
    result = test_client.get(url)
    assert result.status_code == 200
    url = "/extension-report/extension_js_module/FavaExtTest.js"
    result = test_client.get(url)
    assert result.status_code == 200
    url = "/extension-report/extension_js_module/Missing.js"
    result = test_client.get(url)
    assert result.status_code == 404
    url = "/extension-report/extension/MissingExtension/"
    result = test_client.get(url)
    assert result.status_code == 404
