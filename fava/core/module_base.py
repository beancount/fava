"""Base class for the "modules" of FavaLedger."""


class FavaModule:
    """Base class for the "modules" of FavaLedger."""

    def __init__(self, ledger):
        self.ledger = ledger

    def load_file(self):
        """Gets called when the file has been (re)loaded."""
