"""Formatting numbers."""
import copy
from typing import Dict
from typing import Optional

from babel.core import Locale  # type: ignore
from beancount.core.display_context import Precision
from beancount.core.number import Decimal

from fava.core.module_base import FavaModule


def get_pattern(locale, precision: Optional[int]):
    """Obtain formatting pattern for the given locale and precision."""
    if precision and precision > 14:
        # Set a maximum precision of 14, half the default precision of Decimal
        precision = 14
    if locale is None:
        return "{:." + str(precision) + "f}"

    pattern = copy.copy(locale.decimal_formats.get(None))
    pattern.frac_prec = (precision, precision)
    return pattern


class DecimalFormatModule(FavaModule):
    """Formatting numbers."""

    def __init__(self, ledger) -> None:
        super().__init__(ledger)
        self.locale = None
        self.patterns: Dict[str, str] = {}
        self.default_pattern = "{:.2f}"

    def load_file(self) -> None:
        self.locale = None

        locale_option = self.ledger.fava_options["locale"]
        if self.ledger.options["render_commas"] and not locale_option:
            locale_option = "en"
            self.ledger.fava_options["locale"] = locale_option

        if locale_option:
            self.locale = Locale.parse(locale_option)

        self.default_pattern = get_pattern(self.locale, 2)

        dcontext = self.ledger.options["dcontext"]
        for currency, ccontext in dcontext.ccontexts.items():
            precision = ccontext.get_fractional(Precision.MOST_COMMON)
            self.patterns[currency] = get_pattern(self.locale, precision)

    def __call__(self, value: Decimal, currency=None) -> str:
        """Format a decimal to the right number of decimal digits with locale.

        Arguments:
            value: A decimal number.
            currency: A currency string or None.

        Returns:
            A string, the formatted decimal.
        """
        pattern = self.patterns.get(currency, self.default_pattern)
        if not self.locale:
            return pattern.format(value)
        return pattern.apply(value, self.locale)
