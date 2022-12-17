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
        self._names: dict[str, str] = {}
        self.precisions: dict[str, int] = {}

    def load_file(self) -> None:
        self._names = {}
        self.precisions = {}
        for commodity in self.ledger.all_entries_by_type.Commodity:
            name = commodity.meta.get("name")
            if name:
                self._names[commodity.currency] = name
            precision = commodity.meta.get("precision")
            if precision is not None:
                try:
                    self.precisions[commodity.currency] = int(precision)
                except ValueError:
                    pass

    def name(self, commodity: str) -> str:
        """Get the name of a commodity (or the commodity itself if not set)."""
        return self._names.get(commodity, commodity)
