from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def test_commodity_names(example_ledger: FavaLedger) -> None:
    assert example_ledger.commodities.name("USD") == "US Dollar"
    assert example_ledger.commodities.name("NOCOMMODITY") == "NOCOMMODITY"
    assert example_ledger.commodities.name("VMMXX") == "VMMXX"


def test_commodity_precision(example_ledger: FavaLedger) -> None:
    assert example_ledger.commodities.precisions == {
        "USD": 2,
        "VMMXX": 4,
        "VACHR": 0,
    }
