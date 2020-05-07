"""Specify types for the flask application context."""
from typing import Any
from typing import Optional

import flask

from fava.util.date import Interval


class Context:
    """The allowed context values."""

    beancount_file_slug: Optional[str]
    conversion: str
    interval: Interval
    ledger: Any
    partial: bool


g: Context = flask.g
