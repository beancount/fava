from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from babel.core import Locale

from fava.core.number import get_locale_format

if TYPE_CHECKING:  # pragma: no cover
    import pytest

    from fava.core import FavaLedger


def test_get_locale_format() -> None:
    locale = Locale.parse("da_DK")
    dec = Decimal("1.00")
    fmt = get_locale_format(locale, 100)
    assert fmt(dec) == "1,00000000000000"
    fmt = get_locale_format(locale, 14)
    assert fmt(dec) == "1,00000000000000"


def test_precisions(example_ledger: FavaLedger) -> None:
    fmt = example_ledger.format_decimal
    assert fmt.precisions == {
        "ABC": 0,
        "GLD": 0,
        "IRAUSD": 2,
        "ITOT": 0,
        "RGAGX": 3,
        "USD": 2,
        "VACHR": 0,
        "VBMPX": 3,
        "VMMXX": 4,
        "VEA": 0,
        "VHT": 0,
        "XYZ": 0,
    }


def test_format_decimal(example_ledger: FavaLedger) -> None:
    fmt = example_ledger.format_decimal
    assert fmt(Decimal("12.333"), "USD") == "12.33"
    assert fmt(Decimal("12.33"), "USD") == "12.33"
    assert fmt(Decimal("12341234.33"), "USD") == "12341234.33"
    assert fmt(Decimal("12.333"), None) == "12.33"


def test_format_decimal_locale(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fmt = example_ledger.format_decimal
    assert fmt(Decimal("1111111.333"), "USD") == "1111111.33"

    monkeypatch.setattr(example_ledger.fava_options, "locale", "en_IN")
    fmt.load_file()
    assert fmt(Decimal("1111111.333"), "USD") == "11,11,111.33"
    assert fmt(Decimal("11.333"), "USD") == "11.33"
    assert fmt(Decimal("11.3333"), None) == "11.33"

    monkeypatch.setattr(example_ledger.fava_options, "locale", "de_DE")
    fmt.load_file()
    assert fmt(Decimal("1111111.333"), "USD") == "1.111.111,33"

    monkeypatch.undo()
    fmt.load_file()
    assert fmt(Decimal("1111111.333"), "USD") == "1111111.33"
