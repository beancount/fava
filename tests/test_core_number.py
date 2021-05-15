# pylint: disable=missing-docstring
from babel.core import Locale  # type: ignore
from beancount.core.number import D

from fava.core.number import get_pattern


def test_get_pattern() -> None:
    locale = Locale.parse("da_DK")
    high_prec_pattern = get_pattern(locale, 100)
    dec = D("1.00")
    assert high_prec_pattern.apply(dec, locale) == "1,00000000000000"


def test_format_decimal(example_ledger) -> None:
    fmt = example_ledger.format_decimal
    assert fmt(D("12.333"), "USD") == "12.33"
    assert fmt(D("12.33"), "USD") == "12.33"
    assert fmt(D("12341234.33"), "USD") == "12341234.33"
    assert fmt(D("12.333"), None) == "12.33"


def test_format_decimal_locale(example_ledger, monkeypatch) -> None:
    fmt = example_ledger.format_decimal

    monkeypatch.setitem(example_ledger.fava_options, "locale", "en_IN")
    fmt.load_file()
    assert fmt(D("1111111.333"), "USD") == "11,11,111.33"
    assert fmt(D("11.333"), "USD") == "11.33"
    assert fmt(D("11.3333"), None) == "11.33"

    monkeypatch.setitem(example_ledger.fava_options, "locale", "de_DE")
    fmt.load_file()
    assert fmt(D("1111111.333"), "USD") == "1.111.111,33"

    monkeypatch.setitem(example_ledger.fava_options, "locale", "da_DK")
    fmt.load_file()
    dec = D("1.2500000000000000000000000000000000000000000000000000000000")
    monkeypatch.setattr(fmt.patterns["USD"], "frac_prec", (14, 14))
    assert fmt(dec, "USD") == "1,25000000000000"

    fmt.load_file()
