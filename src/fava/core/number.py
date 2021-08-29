"""Formatting numbers."""
import copy
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING

from babel.core import Locale  # type: ignore
from beancount.core.display_context import Precision
from beancount.core.number import Decimal

from fava.core.module_base import FavaModule

if TYPE_CHECKING:
    from fava.core import FavaLedger

Formatter = Callable[[Decimal], str]


def get_locale_format(locale: Optional[Locale], precision: int) -> Formatter:
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
    pattern.frac_prec = (precision, precision)

    def locale_fmt(num: Decimal) -> str:
        return pattern.apply(num, locale)  # type: ignore

    return locale_fmt


class DecimalFormatModule(FavaModule):
    """Formatting numbers."""

    def __init__(self, ledger: "FavaLedger") -> None:
        super().__init__(ledger)
        self.locale = None
        self.formatters: Dict[str, Formatter] = {}
        self.default_pattern = get_locale_format(None, 2)

    def load_file(self) -> None:
        self.locale = None

        locale_option = self.ledger.fava_options["locale"]
        if self.ledger.options["render_commas"] and not locale_option:
            locale_option = "en"
            self.ledger.fava_options["locale"] = locale_option

        if locale_option:
            self.locale = Locale.parse(locale_option)

        self.default_pattern = get_locale_format(self.locale, 2)

        dcontext = self.ledger.options["dcontext"]
        for currency, ccontext in dcontext.ccontexts.items():
            prec = ccontext.get_fractional(Precision.MOST_COMMON)
            if prec is not None:
                self.formatters[currency] = get_locale_format(
                    self.locale, prec
                )

    def __call__(self, value: Decimal, currency: Optional[str] = None) -> str:
        """Format a decimal to the right number of decimal digits with locale.

        Arguments:
            value: A decimal number.
            currency: A currency string or None.

        Returns:
            A string, the formatted decimal.
        """
        if currency is None:
            return self.default_pattern(value)
        return self.formatters.get(currency, self.default_pattern)(value)
