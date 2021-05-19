"""Base class for the "modules" of FavaLedger."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fava.core import FavaLedger


class FavaModule:
    """Base class for the "modules" of FavaLedger."""

    def __init__(self, ledger: "FavaLedger"):
        self.ledger = ledger

    def load_file(self) -> None:
        """Gets called when the file has been (re)loaded."""
