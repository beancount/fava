"""Base class for the "modules" of rustfavaLedger."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.core import RustfavaLedger


class FavaModule:
    """Base class for the "modules" of rustfavaLedger."""

    def __init__(self, ledger: RustfavaLedger) -> None:
        self.ledger = ledger

    def load_file(self) -> None:
        """Run when the file has been (re)loaded."""
