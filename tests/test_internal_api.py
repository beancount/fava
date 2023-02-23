"""Tests for Fava's main Flask app."""
from __future__ import annotations

import copy

from flask import Flask

from fava.core.charts import PRETTY_ENCODER
from fava.internal_api import get_ledger_data

from .conftest import SnapshotFunc

dumps = PRETTY_ENCODER.encode


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
        snapshot(dumps(ledger_data))
