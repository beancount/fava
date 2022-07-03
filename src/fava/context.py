"""Specify types for the flask application context."""
from __future__ import annotations

from flask import g as flask_g

from fava.core import FavaLedger
from fava.core import FilteredLedger
from fava.util.date import Interval


class Context:
    """The allowed context values."""

    beancount_file_slug: str | None
    conversion: str
    interval: Interval
    ledger: FavaLedger
    filtered: FilteredLedger


g: Context = flask_g  # type: ignore
