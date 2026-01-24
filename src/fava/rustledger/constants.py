"""Type constants for rustledger - replaces beancount type constants."""

from __future__ import annotations

from enum import Enum


# Account type sentinel - used in Custom entries to identify account values
# This matches beancount's '<AccountDummy>' sentinel
ACCOUNT_TYPE = "<AccountDummy>"


class Booking(Enum):
    """Booking methods for inventory reduction."""

    STRICT = "STRICT"
    STRICT_WITH_SIZE = "STRICT_WITH_SIZE"
    FIFO = "FIFO"
    LIFO = "LIFO"
    HIFO = "HIFO"
    AVERAGE = "AVERAGE"
    NONE = "NONE"


class Missing:
    """Sentinel for missing/incomplete posting amounts.

    This represents an amount that should be interpolated by the booking system.
    """

    _instance: Missing | None = None

    def __new__(cls) -> Missing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"

    def __bool__(self) -> bool:
        return False


# Singleton instance
MISSING = Missing()


# All directive type names
ALL_DIRECTIVES = frozenset([
    "Transaction",
    "Balance",
    "Open",
    "Close",
    "Commodity",
    "Pad",
    "Event",
    "Query",
    "Note",
    "Document",
    "Price",
    "Custom",
    # Rustledger prefixed versions
    "RLTransaction",
    "RLBalance",
    "RLOpen",
    "RLClose",
    "RLCommodity",
    "RLPad",
    "RLEvent",
    "RLQuery",
    "RLNote",
    "RLDocument",
    "RLPrice",
    "RLCustom",
])
