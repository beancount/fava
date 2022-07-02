# pylint: disable=missing-docstring
from __future__ import annotations

from fava.core import FavaLedger


def test_commodity_names(example_ledger: FavaLedger) -> None:
    assert example_ledger.commodities.name("USD") == "US Dollar"
    assert example_ledger.commodities.name("NOCOMMODITY") == "NOCOMMODITY"
    assert example_ledger.commodities.name("VMMXX") == "VMMXX"


def test_commodity_precision(example_ledger: FavaLedger) -> None:
    assert example_ledger.commodities.precision("USD") == 2
    assert example_ledger.commodities.precision("VMMXX") == 4
    assert example_ledger.commodities.precision("IRAUSD") is None
    assert example_ledger.commodities.precision("NOCOMMODITY") is None
