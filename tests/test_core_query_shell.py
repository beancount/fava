from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.beans.funcs import run_query
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


def test_query(snapshot: SnapshotFunc, get_ledger: GetFavaLedger) -> None:
    query_ledger = get_ledger("query-example")

    def run(query_string: str) -> Any:
        return query_ledger.query_shell.execute_query(
            query_ledger.all_entries,
            query_string,
        )

    def run_text(query_string: str) -> str:
        """Run a query that should only return string contents."""
        contents, types, result = run(query_string)
        assert types is None
        assert result is None
        assert isinstance(contents, str)
        return contents

    assert run_text("help")
    assert run_text("print")
    assert run_text("exit") == "Doesn't do anything in Fava's query shell."
    assert (
        run_text("help exit") == "Doesn't do anything in Fava's query shell."
    )
    snapshot(run_text("explain select date, balance"))
    assert (
        run("lex select date, balance")[0]
        == "LexToken(SELECT,'SELECT',1,0)\nLexToken(ID,'date',1,7)\nL"
        "exToken(COMMA,',',1,11)\nLexToken(ID,'balance',1,13)"
    )

    assert run_text("run") == "custom_query\ncustom query with space"
    bal = run("balances")
    snapshot(bal)

    various_types = run(
        "select date, payee, weight, change, balance, "
        "cost_number, coalesce(cost_number, 1), tags"
    )
    assert len(various_types[1]) == 8

    assert run("run custom_query") == bal
    assert run("run 'custom query with space'") == bal
    assert run("balances")[1:] == run_query(
        query_ledger.all_entries,
        query_ledger.options,
        "balances",
    )
    assert (
        run_text("asdf")
        == "ERROR: Syntax error near 'asdf' (at 0)\n  asdf\n  ^"
    )


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

    with pytest.raises(FavaAPIError):
        query_shell.query_to_file(entries, "select sdf", "csv")

    with pytest.raises(FavaAPIError):
        query_shell.query_to_file(entries, "run testsetest", "csv")
