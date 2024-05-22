"""Formatting numbers."""

from __future__ import annotations

import copy
from decimal import Decimal
from typing import Callable
from typing import TYPE_CHECKING

from babel.core import Locale
from beancount.core.display_context import Precision

from fava.core.module_base import FavaModule

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

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
    if not pattern:
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
        if self.ledger.options["render_commas"] and not locale_option:
            locale_option = "en"
            self.ledger.fava_options.locale = locale_option

        if locale_option:
            locale = Locale.parse(locale_option)

        dcontext = self.ledger.options["dcontext"]
        precisions: dict[str, int] = {}
        for currency, ccontext in dcontext.ccontexts.items():
            prec = ccontext.get_fractional(Precision.MOST_COMMON)
            if prec is not None:
                precisions[currency] = prec
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
