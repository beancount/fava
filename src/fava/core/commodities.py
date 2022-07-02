"""Attributes for auto-completion."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


class CommoditiesModule(FavaModule):
    """Details about the currencies and commodities."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self._commodity_names: dict[str, str] = {}

    def load_file(self) -> None:
        self._commodity_names = {}
        for commodity in self.ledger.all_entries_by_type.Commodity:
            name = commodity.meta.get("name")
            if name:
                self._commodity_names[commodity.currency] = name

    def name(self, commodity: str) -> str:
        return self._commodity_names.get(commodity, commodity)
