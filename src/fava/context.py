"""Specify types for the flask application context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g as flask_g

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger
    from fava.core import FilteredLedger
    from fava.core.conversion import Conversion
    from fava.ext import FavaExtensionBase
    from fava.util.date import Interval


class Context:
    """The allowed context values."""

    #: Slug for the active Beancount file.
    beancount_file_slug: str | None
    #: Conversion to apply (raw string)
    conversion: str
    #: Conversion to apply (parsed)
    conv: Conversion
    #: Interval to group by
    interval: Interval
    #: The ledger
    ledger: FavaLedger
    #: The filtered ledger
    filtered: FilteredLedger
    #: The current extension, if this is an extension endpoint
    extension: FavaExtensionBase | None


g: Context = flask_g  # type: ignore[assignment]
