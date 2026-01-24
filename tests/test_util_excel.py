from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest

from rustfava.rustledger.query import connect
from rustfava.util import excel

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.core import RustfavaLedger


def _run_query(ledger: RustfavaLedger, query: str) -> Any:
    """Run a query using rustledger and return types/rows for excel export."""
    conn = connect(
        "rustledger:",
        entries=ledger.all_entries,
        options=ledger.options,
        errors=ledger.errors,
    )
    # Set source for queries
    source = getattr(ledger, "_source", None)
    if source:
        conn.set_source(source)

    curs = conn.execute(query)
    rrows = curs.fetchall()
    rtypes = list(curs.description)
    return rtypes, rrows


def test_to_csv(example_ledger: RustfavaLedger) -> None:
    types, rows = _run_query(example_ledger, "balances")
    assert types
    assert rows
    assert excel.to_csv(types, rows)
    types, rows = _run_query(example_ledger, "select account, tags, date, day")
    assert types
    assert rows
    assert excel.to_csv(types, rows)


@pytest.mark.skipif(not excel.HAVE_EXCEL, reason="pyexcel not installed")
def test_to_excel(example_ledger: RustfavaLedger) -> None:
    types, rows = _run_query(example_ledger, "balances")
    assert types
    assert rows
    assert excel.to_excel(types, rows, "ods", "balances")
