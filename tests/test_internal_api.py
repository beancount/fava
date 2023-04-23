"""Tests for Fava's main Flask app."""
from __future__ import annotations

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
        snapshot(pretty_dumps(get_ledger_data()))
