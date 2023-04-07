"""Tests for Fava's main Flask app."""
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from fava.core.charts import pretty_dumps
from fava.internal_api import get_ledger_data

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask

    from .conftest import SnapshotFunc


def test_get_ledger_data(app: Flask, snapshot: SnapshotFunc) -> None:
    """The currently filtered journal can be downloaded."""
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        ledger_data = copy.copy(get_ledger_data())
        # Overwrite this testenv-dependant value
        ledger_data.have_excel = False
        for details in ledger_data.account_details.values():
            if details.last_entry:
                details.last_entry.entry_hash = "ENTRY_HASH"
        snapshot(pretty_dumps(ledger_data))
