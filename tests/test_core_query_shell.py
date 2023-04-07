# pylint: disable=missing-docstring
from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.beans.funcs import run_query
from fava.helpers import FavaAPIException

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

    from .conftest import SnapshotFunc


def test_query(snapshot: SnapshotFunc, query_ledger: FavaLedger) -> None:
    def run(query_string: str) -> Any:
        return query_ledger.query_shell.execute_query(
            query_ledger.all_entries, query_string
        )

    def run_text(query_string: str) -> str:
        """Run a query that should only return string contents."""
        contents, types, result = run(query_string)
        assert types is None
        assert result is None
        assert isinstance(contents, str)
        return contents

    assert run_text("help")
    assert (
        run_text("help exit") == "Doesn't do anything in Fava's query shell."
    )
    snapshot(run_text("explain select date, balance"))
    assert run("lex select date, balance")[0] == "\n".join(
        [
            "LexToken(SELECT,'SELECT',1,0)",
            "LexToken(ID,'date',1,7)",
            "LexToken(COMMA,',',1,11)",
            "LexToken(ID,'balance',1,13)",
        ]
    )

    assert run_text("run") == "custom_query\ncustom query with space"
    bal = run("balances")
    snapshot(bal)
    assert run("run custom_query") == bal
    assert run("run 'custom query with space'") == bal
    assert run("balances")[1:] == run_query(
        query_ledger.all_entries, query_ledger.options, "balances"
    )
    assert (
        run_text("asdf")
        == "ERROR: Syntax error near 'asdf' (at 0)\n  asdf\n  ^"
    )


def test_query_to_file(
    snapshot: SnapshotFunc, query_ledger: FavaLedger
) -> None:
    entries = query_ledger.all_entries
    query_shell = query_ledger.query_shell
    name, data = query_shell.query_to_file(entries, "run custom_query", "csv")
    assert name == "custom_query"
    name, data = query_shell.query_to_file(entries, "balances", "csv")
    assert name == "query_result"
    snapshot(data.getvalue())

    with pytest.raises(FavaAPIException):
        query_shell.query_to_file(entries, "select sdf", "csv")

    with pytest.raises(FavaAPIException):
        query_shell.query_to_file(entries, "run testsetest", "csv")
