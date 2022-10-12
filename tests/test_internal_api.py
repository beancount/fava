"""Tests for Fava's main Flask app."""
from __future__ import annotations

from flask import Flask

from .conftest import SnapshotFunc
from fava.core.charts import PRETTY_ENCODER
from fava.internal_api import get_ledger_data


dumps = PRETTY_ENCODER.encode


def test_get_ledger_data(app: Flask, snapshot: SnapshotFunc) -> None:
    """The currently filtered journal can be downloaded."""
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        ledger_data = get_ledger_data()
        # Overwrite this testenv-dependant value
        ledger_data.have_excel = False
        snapshot(dumps(ledger_data))
