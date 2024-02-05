"""Specify types for the flask application context."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from flask import request

from fava.core.conversion import conversion_from_str
from fava.util.date import Interval

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger
    from fava.core import FilteredLedger
    from fava.core.conversion import Conversion
    from fava.ext import FavaExtensionBase


class Context:
    """The context values - this is used for `flask.g`."""

    #: Slug for the active Beancount file.
    beancount_file_slug: str | None
    #: The ledger
    ledger: FavaLedger
    #: The current extension, if this is an extension endpoint
    extension: FavaExtensionBase | None

    @cached_property
    def conversion(self) -> str:
        """Conversion to apply (raw string)."""
        return request.args.get("conversion", "") or "at_cost"

    @cached_property
    def conv(self) -> Conversion:
        """Conversion to apply (parsed)."""
        return conversion_from_str(self.conversion)

    @cached_property
    def interval(self) -> Interval:
        """Interval to group by."""
        return Interval.get(request.args.get("interval", ""))

    @cached_property
    def filtered(self) -> FilteredLedger:
        """The filtered ledger."""
        args = request.args
        return self.ledger.get_filtered(
            account=args.get("account", ""),
            filter=args.get("filter", ""),
            time=args.get("time", ""),
        )
