"""Attributes for auto-completion."""

from __future__ import annotations

from contextlib import suppress
from decimal import Decimal
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


class CommoditiesModule(FavaModule):
    """Details about the currencies and commodities."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.names: dict[str, str] = {}
        self.precisions: dict[str, int] = {}

    def load_file(self) -> None:  # noqa: D102
        self.names = {}
        self.precisions = {}
        for commodity in self.ledger.all_entries_by_type.Commodity:
            name = commodity.meta.get("name")
            if name:
                self.names[commodity.currency] = str(name)
            precision = commodity.meta.get("precision")
            if isinstance(precision, (str, int, Decimal)):
                with suppress(ValueError):
                    self.precisions[commodity.currency] = int(precision)

    def name(self, commodity: str) -> str:
        """Get the name of a commodity (or the commodity itself if not set)."""
        return self.names.get(commodity, commodity)
