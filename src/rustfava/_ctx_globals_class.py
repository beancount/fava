"""Specify types for the flask application context."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from flask import request

from rustfava.core.conversion import conversion_from_str
from rustfava.util.date import INTERVALS
from rustfava.util.date import Month

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.core import RustfavaLedger
    from rustfava.core import FilteredLedger
    from rustfava.core.conversion import Conversion
    from rustfava.ext import RustfavaExtensionBase
    from rustfava.util.date import Interval


class Context:
    """The context values - this is used for `flask.g`."""

    #: Slug for the active Beancount file.
    beancount_file_slug: str | None
    #: The ledger
    ledger: RustfavaLedger
    #: The current extension, if this is an extension endpoint
    extension: RustfavaExtensionBase | None

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
        return INTERVALS.get(request.args.get("interval", "").lower(), Month)

    @cached_property
    def filtered(self) -> FilteredLedger:
        """The filtered ledger."""
        args = request.args
        return self.ledger.get_filtered(
            account=args.get("account", ""),
            filter=args.get("filter", ""),
            time=args.get("time", ""),
        )
