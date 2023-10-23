"""Tests for Fava's main Flask app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fava.internal_api import ChartApi
from fava.internal_api import get_ledger_data

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask

    from .conftest import SnapshotFunc


def test_get_ledger_data(app: Flask, snapshot: SnapshotFunc) -> None:
    """The currently filtered journal can be downloaded."""
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        snapshot(get_ledger_data(), json=True)


def test_chart_api(app: Flask, snapshot: SnapshotFunc) -> None:
    """The serialisation and generation of charts works."""
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        snapshot([ChartApi.hierarchy("Assets")], json=True)
