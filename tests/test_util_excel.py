# pylint: disable=missing-docstring
from __future__ import annotations

import pytest
from beancount.query.query import run_query

from fava.core import FavaLedger
from fava.util import excel


def test_to_csv(example_ledger: FavaLedger) -> None:
    types, rows = run_query(
        example_ledger.all_entries,
        example_ledger.options,
        "balances",
        numberify=True,
    )
    assert excel.to_csv(types, rows)
    types, rows = run_query(
        example_ledger.all_entries,
        example_ledger.options,
        "select account, tags, date, day",
        numberify=True,
    )
    assert excel.to_csv(types, rows)


@pytest.mark.skipif(not excel.HAVE_EXCEL, reason="pyexcel not installed")
def test_to_excel(example_ledger: FavaLedger) -> None:
    types, rows = run_query(
        example_ledger.all_entries,
        example_ledger.options,
        "balances",
        numberify=True,
    )
    assert excel.to_excel(types, rows, "ods", "balances")
