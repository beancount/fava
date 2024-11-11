from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import beanquery
import pytest

from fava.util import excel

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def _run_query(ledger: FavaLedger, query: str) -> Any:
    conn = beanquery.connect(
        "beancount:",
        entries=ledger.all_entries,
        options=ledger.options,
        errors=ledger.errors,
    )
    curs = conn.execute(query)
    rrows = curs.fetchall()
    rtypes = curs.description
    dformat = ledger.options["dcontext"].build()  # type: ignore[attr-defined]
    rtypes, rrows = beanquery.numberify.numberify_results(
        rtypes, rrows, dformat
    )
    return rtypes, rrows


def test_to_csv(example_ledger: FavaLedger) -> None:
    types, rows = _run_query(example_ledger, "balances")
    assert types
    assert rows
    assert excel.to_csv(types, rows)
    types, rows = _run_query(example_ledger, "select account, tags, date, day")
    assert types
    assert rows
    assert excel.to_csv(types, rows)


@pytest.mark.skipif(not excel.HAVE_EXCEL, reason="pyexcel not installed")
def test_to_excel(example_ledger: FavaLedger) -> None:
    types, rows = _run_query(example_ledger, "balances")
    assert types
    assert rows
    assert excel.to_excel(types, rows, "ods", "balances")
