"""Formatting numbers."""

import copy

from babel.core import Locale, UnknownLocaleError
from beancount.core.display_context import Precision

from fava.core.helpers import FavaModule
from fava.core.fava_options import OptionError


class DecimalFormatModule(FavaModule):
    """Formatting numbers."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.locale = None
        self.patterns = {}
        self.default_pattern = None

    def load_file(self):
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
                self.ledger.errors.append(
                    OptionError(
                        None,
                        "Unknown locale: {}.".format(
                            self.ledger.fava_options["locale"]
                        ),
                        None,
                    )
                )

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

    def __call__(self, value, currency=None):
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
