from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import beanquery
import pytest
from beancount.core import data
from beanquery.numberify import numberify_results

from fava.rustledger.beanquery_compat import to_beancount_entries
from fava.util import excel

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def _run_query(ledger: FavaLedger, query: str) -> Any:
    # Convert rustledger entries to beancount entries for beanquery
    entries = ledger.all_entries
    bc_entries = (
        entries
        if entries and isinstance(entries[0], data.ALL_DIRECTIVES)
        else to_beancount_entries(entries)
    )
    conn = beanquery.connect(
        "beancount:",
        entries=bc_entries,
        options=ledger.options,
        errors=ledger.errors,
    )
    curs = conn.execute(query)
    rrows = curs.fetchall()
    rtypes = curs.description
    dcontext = ledger.options["dcontext"]
    # Duck-type check: DisplayContext can be beancount's or RLDisplayContext
    assert hasattr(dcontext, "build")
    dformat = dcontext.build()
    rtypes, rrows = numberify_results(rtypes, rrows, dformat)
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
