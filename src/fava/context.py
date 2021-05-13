"""Specify types for the flask application context."""
from typing import Optional

import flask

from fava.core import FavaLedger
from fava.util.date import Interval


class Context:
    """The allowed context values."""

    beancount_file_slug: Optional[str]
    conversion: str
    interval: Interval
    ledger: FavaLedger


g: Context = flask.g  # type: ignore
