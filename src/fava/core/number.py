"""Formatting numbers."""
import copy
from typing import Dict

from babel.core import Locale  # type: ignore
from babel.core import UnknownLocaleError
from beancount.core.display_context import Precision
from beancount.core.number import Decimal

from fava.core.fava_options import OptionError
from fava.core.module_base import FavaModule


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
            try:
                self.locale = Locale.parse(locale_option)
            except UnknownLocaleError:
                self.locale = None
                error = OptionError(
                    None,
                    f"Unknown locale: {self.ledger.fava_options['locale']}.",
                    None,
                )
                self.ledger.errors.append(error)

        if self.locale:
            self.default_pattern = copy.copy(
                self.locale.decimal_formats.get(None)
            )
            self.default_pattern.frac_prec = (2, 2)
        else:
            self.default_pattern = "{:.2f}"

        dcontext = self.ledger.options["dcontext"]
        for currency, ccontext in dcontext.ccontexts.items():
            precision = ccontext.get_fractional(Precision.MOST_COMMON)
            if self.locale:
                pattern = copy.copy(self.locale.decimal_formats.get(None))
                pattern.frac_prec = (precision, precision)
            else:
                pattern = "{:." + str(precision) + "f}"
            self.patterns[currency] = pattern

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
