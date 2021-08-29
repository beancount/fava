# pylint: disable=missing-docstring
from babel.core import Locale  # type: ignore
from beancount.core.number import D

from fava.core.number import get_locale_format


def test_get_locale_format() -> None:
    locale = Locale.parse("da_DK")
    dec = D("1.00")
    fmt = get_locale_format(locale, 100)
    assert fmt(dec) == "1,00000000000000"
    fmt = get_locale_format(locale, 14)
    assert fmt(dec) == "1,00000000000000"


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

    fmt.load_file()
