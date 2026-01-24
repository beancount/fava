"""Options adapter for rustledger JSON to Fava's BeancountOptions."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from rustfava.beans.types import BeancountOptions


class _RLCurrencyContext:
    """Minimal CurrencyContext for a single currency."""

    def __init__(self, precision: int) -> None:
        self._precision = precision

    def get_fractional(self, _precision_type: Any = None) -> int:
        """Return the fractional precision (beancount-compatible API)."""
        return self._precision


class RLDisplayContext:
    """Minimal DisplayContext implementation for rustledger.

    This replaces beancount.core.display_context.DisplayContext.
    Provides beancount-compatible `ccontexts` property.
    """

    def __init__(self, options: dict[str, Any]) -> None:
        """Initialize from rustledger options."""
        self._precision = options.get("display_precision", {})
        self._render_commas = options.get("render_commas", True)
        # Beancount-compatible ccontexts mapping
        self.ccontexts = {
            currency: _RLCurrencyContext(prec)
            for currency, prec in self._precision.items()
        }

    def build(self) -> RLDisplayFormatter:
        """Build a formatter from this context."""
        return RLDisplayFormatter(self._precision, self._render_commas)


class RLDisplayFormatter:
    """Formatter for decimal numbers."""

    def __init__(
        self,
        precision: dict[str, int],
        render_commas: bool,
    ) -> None:
        """Initialize formatter."""
        self._precision = precision
        self._render_commas = render_commas

    def format(self, number: Decimal, currency: str) -> str:
        """Format a decimal number for a currency."""
        prec = self._precision.get(currency, 2)
        formatted = f"{number:.{prec}f}"
        if self._render_commas:
            # Add thousand separators
            parts = formatted.split(".")
            parts[0] = "{:,}".format(int(parts[0]))
            formatted = ".".join(parts)
        return formatted

    def quantize(
        self,
        number: Decimal,
        currency: str = "__default__",
    ) -> Decimal:
        """Quantize a number to the precision for a currency.

        This matches beancount's DisplayFormatter.quantize interface.
        """
        prec = self._precision.get(currency, 2)
        # Create a Decimal with the right number of decimal places
        quantizer = Decimal(10) ** -prec
        return number.quantize(quantizer)


class RLBooking:
    """Booking method enum compatible with beancount.core.data.Booking."""

    STRICT = "STRICT"
    FIFO = "FIFO"
    LIFO = "LIFO"
    HIFO = "HIFO"
    AVERAGE = "AVERAGE"
    NONE = "NONE"

    def __init__(self, value: str) -> None:
        """Initialize from string value."""
        self.value = value.upper() if value else "STRICT"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if isinstance(other, str):
            return self.value == other.upper()
        if isinstance(other, RLBooking):
            return self.value == other.value
        return False


def options_from_json(data: dict[str, Any]) -> BeancountOptions:
    """Convert rustledger options JSON to Fava's BeancountOptions.

    Args:
        data: JSON dict of options from rustledger

    Returns:
        BeancountOptions TypedDict
    """
    # Create display context
    dcontext = RLDisplayContext(data)

    # Parse display_precision
    display_precision = {
        k: Decimal(str(v))
        for k, v in data.get("display_precision", {}).items()
    }

    # Parse inferred_tolerance_default
    inferred_tolerance_default = {
        k: Decimal(str(v))
        for k, v in data.get("inferred_tolerance_default", {}).items()
    }

    options: BeancountOptions = {
        "title": data.get("title", ""),
        "filename": data.get("filename", ""),
        # Root account names
        "name_assets": data.get("name_assets", "Assets"),
        "name_liabilities": data.get("name_liabilities", "Liabilities"),
        "name_equity": data.get("name_equity", "Equity"),
        "name_income": data.get("name_income", "Income"),
        "name_expenses": data.get("name_expenses", "Expenses"),
        # Special accounts
        "account_current_conversions": data.get(
            "account_current_conversions", "Equity:Conversions:Current"
        ),
        "account_current_earnings": data.get(
            "account_current_earnings", "Equity:Earnings:Current"
        ),
        "account_previous_balances": data.get(
            "account_previous_balances", "Equity:Opening-Balances"
        ),
        "account_previous_conversions": data.get(
            "account_previous_conversions", "Equity:Conversions:Previous"
        ),
        "account_previous_earnings": data.get(
            "account_previous_earnings", "Equity:Earnings:Previous"
        ),
        "account_rounding": data.get("account_rounding"),
        "account_unrealized_gains": data.get(
            "account_unrealized_gains", "Income:Unrealized"
        ),
        # Booking and commodities
        "booking_method": RLBooking(data.get("booking_method", "STRICT")),
        "commodities": set(data.get("commodities", [])),
        "conversion_currency": data.get("conversion_currency", ""),
        "dcontext": dcontext,  # type: ignore[typeddict-item]
        "display_precision": display_precision,
        # File handling
        "documents": list(data.get("documents", [])),
        "include": list(data.get("include", [])),
        # Tolerances
        "infer_tolerance_from_cost": data.get("infer_tolerance_from_cost", False),
        "inferred_tolerance_default": inferred_tolerance_default,
        "inferred_tolerance_multiplier": Decimal(
            str(data.get("inferred_tolerance_multiplier", "0.5"))
        ),
        "input_hash": data.get("input_hash", ""),
        "insert_pythonpath": data.get("insert_pythonpath", False),
        "operating_currency": list(data.get("operating_currency", [])),
        # Plugins (won't work with rustledger, but keep for compatibility)
        "plugin": list(
            tuple(p) if isinstance(p, list) else (p, None)
            for p in data.get("plugin", [])
        ),
        "plugin_processing_mode": data.get("plugin_processing_mode", ""),
        "pythonpath": list(data.get("pythonpath", [])),
        "render_commas": data.get("render_commas", False),
        "tolerance_multiplier": Decimal(
            str(data.get("tolerance_multiplier", "1.0"))
        ),
        # Deprecated options (for compatibility)
        "allow_deprecated_none_for_tags_and_links": data.get(
            "allow_deprecated_none_for_tags_and_links", False
        ),
        "allow_pipe_separator": data.get("allow_pipe_separator", False),
        "long_string_maxlines": data.get("long_string_maxlines", 64),
    }

    return options
