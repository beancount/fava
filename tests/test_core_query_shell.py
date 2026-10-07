from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import suppress
from threading import Event
from typing import TYPE_CHECKING

import pytest

from fava.core.query import QueryResultTable
from fava.core.query import QueryResultText
from fava.core.query_shell import NonExportableQueryError
from fava.core.query_shell import QueryCompilationError
from fava.core.query_shell import QueryNotFoundError
from fava.core.query_shell import QueryParseError
from fava.core.query_shell import TooManyRunArgsError
from fava.util import excel

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from fava.core import FavaLedger
    from fava.core.query import QueryResult

    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


@pytest.fixture
def run_query(get_ledger: GetFavaLedger) -> Callable[[str], QueryResult]:
    query_ledger = get_ledger("query-example")

    def _run_query(query_string: str) -> QueryResult:
        return query_ledger.query_shell.execute_query_serialised(
            query_ledger.all_entries,
            query_string,
        )

    return _run_query


@pytest.fixture
def run_text_query(
    run_query: Callable[[str], QueryResult],
) -> Callable[[str], str]:
    def _run_text_query(query_string: str) -> str:
        """Run a query that should only return string contents."""
        result = run_query(query_string)
        assert isinstance(result, QueryResultText)
        return result.contents

    return _run_text_query


def test_text_queries(
    snapshot: SnapshotFunc, run_text_query: Callable[[str], str]
) -> None:
    assert run_text_query(".help")

    noop_doc = "Doesn't do anything in Fava's query shell."
    assert run_text_query(".exit") == noop_doc
    assert run_text_query(".help exit") == noop_doc
    snapshot(run_text_query(".explain select date, balance")[:100])

    assert run_text_query(".run") == "custom_query\ncustom query with space"


def test_query_balances(
    snapshot: SnapshotFunc, run_query: Callable[[str], QueryResult]
) -> None:
    assert isinstance(run_query(".run custom_query"), QueryResultTable)
    bal = run_query("balances")
    if sys.version_info >= (3, 12):
        # This fails for some reason on older Pythons, probably some minor
        # difference there.
        snapshot(bal, json=True)
    assert run_query(".run custom_query") == bal
    assert run_query(".run 'custom query with space'") == bal


@pytest.mark.parametrize("second_result_format", ["json", "csv"])
def test_concurrent_queries(
    small_example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
    second_result_format: str,
) -> None:
    ledger = small_example_ledger
    query_shell = ledger.query_shell
    first_entries = ledger.get_filtered(time="2012-11").entries
    second_entries = ledger.get_filtered(time="2012-12").entries
    query = "SELECT count(*)"
    expected_first = query_shell.execute_query_serialised(first_entries, query)

    def run_second() -> QueryResult | bytes:
        if second_result_format == "csv":
            _, data = query_shell.query_to_file(second_entries, query, "csv")
            return data.getvalue()
        return query_shell.execute_query_serialised(second_entries, query)

    expected_second = run_second()
    first_started = Event()
    release_first = Event()
    original_onecmd = query_shell.shell.onecmd

    def onecmd(query: str) -> object:
        if not first_started.is_set():
            first_started.set()
            assert release_first.wait(timeout=5)
        return original_onecmd(query)  # type: ignore[no-untyped-call]

    monkeypatch.setattr(query_shell.shell, "onecmd", onecmd)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            query_shell.execute_query_serialised, first_entries, query
        )
        try:
            assert first_started.wait(timeout=5)
            second = pool.submit(run_second)
            # An unprotected second query can finish while the first is paused.
            # A protected query waits until the first is released instead.
            with suppress(FutureTimeoutError):
                second.result(timeout=0.5)
        finally:
            release_first.set()
        assert first.result(timeout=5) == expected_first
        assert second.result(timeout=5) == expected_second


def test_query_types(run_query: Callable[[str], QueryResult]) -> None:
    various_types = run_query(
        "select date, payee, weight, position, balance, "
        "cost_number, cost_number, tags, entry, meta"
    )
    assert isinstance(various_types, QueryResultTable)
    assert len(various_types.types) == 10


def test_query_errors(run_query: Callable[[str], QueryResult]) -> None:
    with pytest.raises(TooManyRunArgsError):
        run_query(".run custom_query other")
    with pytest.raises(QueryNotFoundError):
        run_query(".run unknown")
    with pytest.raises(QueryParseError):
        run_query("asdf")
    with pytest.raises(QueryCompilationError):
        run_query("select asdf")


def test_query_to_file(
    snapshot: SnapshotFunc,
    get_ledger: GetFavaLedger,
) -> None:
    query_ledger = get_ledger("query-example")
    entries = query_ledger.all_entries
    query_shell = query_ledger.query_shell

    name, data = query_shell.query_to_file(entries, "run custom_query", "csv")
    assert name == "custom_query"
    name, data = query_shell.query_to_file(entries, "balances", "csv")
    assert name == "query_result"
    snapshot(data.getvalue())

    with pytest.raises(NonExportableQueryError):
        query_shell.query_to_file(entries, ".help targets", "csv")
    with pytest.raises(TooManyRunArgsError):
        query_shell.query_to_file(entries, "run custom_query other", "csv")
    with pytest.raises(QueryNotFoundError):
        query_shell.query_to_file(entries, "run testsetest", "csv")
    with pytest.raises(QueryParseError):
        query_shell.query_to_file(entries, "asdf", "csv")
    with pytest.raises(QueryCompilationError):
        query_shell.query_to_file(entries, "select asdf", "csv")


@pytest.mark.skipif(not excel.HAVE_EXCEL, reason="pyexcel not installed")
def test_query_to_excel_file(get_ledger: GetFavaLedger) -> None:
    query_ledger = get_ledger("query-example")
    entries = query_ledger.all_entries
    query_shell = query_ledger.query_shell

    name, _data = query_shell.query_to_file(entries, "run custom_query", "ods")
    assert name == "custom_query"
