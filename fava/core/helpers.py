"""Exceptions and module base class."""

from typing import Any
from typing import NamedTuple


class BeancountError(NamedTuple):
    """NamedTuple base for a Beancount-style error."""

    source: Any
    message: str
    entry: Any


class FavaAPIException(Exception):
    """Fava's base exception class."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message


class FilterException(FavaAPIException):
    """Filter exception."""

    def __init__(self, filter_type: str, message: str) -> None:
        super().__init__(message)
        self.filter_type = filter_type

    def __str__(self) -> str:
        return self.message


class FavaModule:
    """Base class for the "modules" of FavaLedger."""

    def __init__(self, ledger):
        self.ledger = ledger

    def load_file(self):
        """Gets called when the file has been (re)loaded."""
