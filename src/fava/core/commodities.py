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
        self._precisions: dict[str, int] = {}

    def load_file(self) -> None:
        self._names = {}
        for commodity in self.ledger.all_entries_by_type.Commodity:
            name = commodity.meta.get("name")
            if name:
                self._names[commodity.currency] = name
            precision = commodity.meta.get("precision")
            if precision:
                try:
                    self._precisions[commodity.currency] = int(precision)
                except ValueError:
                    pass

    def name(self, commodity: str) -> str:
        return self._names.get(commodity, commodity)

    def precision(self, commodity: str) -> int | None:
        return self._precisions.get(commodity)
