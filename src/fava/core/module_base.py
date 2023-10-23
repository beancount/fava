"""Base class for the "modules" of FavaLedger."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


class FavaModule:
    """Base class for the "modules" of FavaLedger."""

    def __init__(self, ledger: FavaLedger) -> None:
        self.ledger = ledger

    def load_file(self) -> None:
        """Run when the file has been (re)loaded."""
