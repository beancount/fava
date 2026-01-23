"""Formatting numbers."""

from __future__ import annotations

import copy
from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

from babel.core import Locale

from fava.core.module_base import FavaModule

# Try to import beancount's DisplayContext, but don't fail if unavailable
try:
    from beancount.core.display_context import DisplayContext
    from beancount.core.display_context import Precision
except ImportError:
    DisplayContext = None  # type: ignore[misc,assignment]
    Precision = None  # type: ignore[misc,assignment]

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def _get_decimal_places(number: Decimal) -> int:
    """Get the number of decimal places in a Decimal."""
    sign, digits, exponent = number.as_tuple()
    if isinstance(exponent, int) and exponent < 0:
        return -exponent
    return 0


def _infer_precisions_from_entries(ledger: FavaLedger) -> dict[str, int]:
    """Infer currency precisions from transaction amounts.

    This mimics beancount's DisplayContext behavior by finding the
    most commonly used precision for each currency.
    """
    # Count occurrences of each precision for each currency
    precision_counts: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))

    for txn in ledger.all_entries_by_type.Transaction:
        for posting in txn.postings:
            if posting.units is not None:
                currency = posting.units.currency
                prec = _get_decimal_places(posting.units.number)
                precision_counts[currency][prec] += 1
            if posting.cost is not None and posting.cost.number is not None:
                currency = posting.cost.currency
                prec = _get_decimal_places(posting.cost.number)
                precision_counts[currency][prec] += 1

    # Also check Balance directives
    for bal in ledger.all_entries_by_type.Balance:
        currency = bal.amount.currency
        prec = _get_decimal_places(bal.amount.number)
        precision_counts[currency][prec] += 1

    # Find most common precision for each currency
    precisions: dict[str, int] = {}
    for currency, counts in precision_counts.items():
        if counts:
            # Get the precision with the highest count
            most_common_prec = max(counts.keys(), key=lambda p: counts[p])
            precisions[currency] = most_common_prec

    return precisions

Formatter = Callable[[Decimal], str]


def get_locale_format(locale: Locale | None, precision: int) -> Formatter:
    """Obtain formatting pattern for the given locale and precision.

    Arguments:
        locale: An optional locale.
        precision: The precision.

    Returns:
        A function that renders Decimals to strings as desired.
    """
    # Set a maximum precision of 14, half the default precision of Decimal
    precision = min(precision, 14)
    if locale is None:
        fmt_string = "{:." + str(precision) + "f}"

        def fmt(num: Decimal) -> str:
            return fmt_string.format(num)

        return fmt

    pattern = copy.copy(locale.decimal_formats.get(None))
    if not pattern:  # pragma: no cover
        msg = "Expected Locale to have a decimal format pattern"
        raise ValueError(msg)
    pattern.frac_prec = (precision, precision)

    def locale_fmt(num: Decimal) -> str:
        return pattern.apply(num, locale)  # type: ignore[no-any-return]

    return locale_fmt


class DecimalFormatModule(FavaModule):
    """Formatting numbers."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self._locale: Locale | None = None
        self._formatters: dict[str, Formatter] = {}
        self._default_pattern = get_locale_format(None, 2)
        self.precisions: dict[str, int] = {}

    def load_file(self) -> None:  # noqa: D102
        locale = None

        locale_option = self.ledger.fava_options.locale
        if (
            self.ledger.options["render_commas"] and not locale_option
        ):  # pragma: no cover
            locale_option = "en"
            self.ledger.fava_options.locale = locale_option

        if locale_option:
            locale = Locale.parse(locale_option)

        dcontext = self.ledger.options["dcontext"]
        precisions: dict[str, int] = {}

        # Handle both beancount's DisplayContext and rustledger's RLDisplayContext
        if DisplayContext is not None and isinstance(dcontext, DisplayContext):
            for currency, ccontext in dcontext.ccontexts.items():
                prec = ccontext.get_fractional(Precision.MOST_COMMON)
                if prec is not None:
                    precisions[currency] = prec
        else:
            # Infer precisions from transaction amounts (for rustledger)
            precisions.update(_infer_precisions_from_entries(self.ledger))

        precisions.update(self.ledger.commodities.precisions)

        self._locale = locale
        self._default_pattern = get_locale_format(locale, 2)
        self._formatters = {
            currency: get_locale_format(locale, prec)
            for currency, prec in precisions.items()
        }
        self.precisions = precisions

    def __call__(self, value: Decimal, currency: str | None = None) -> str:
        """Format a decimal to the right number of decimal digits with locale.

        Arguments:
            value: A decimal number.
            currency: A currency string or None.

        Returns:
            A string, the formatted decimal.
        """
        if currency is None:
            return self._default_pattern(value)
        return self._formatters.get(currency, self._default_pattern)(value)
