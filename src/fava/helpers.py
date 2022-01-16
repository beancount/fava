"""Exceptions and module base class."""
from __future__ import annotations

from typing import Any
from typing import NamedTuple

from beancount.core.data import Directive


class BeancountError(NamedTuple):
    """NamedTuple base for a Beancount-style error."""

    source: Any
    message: str
    entry: Directive | None


class FavaAPIException(Exception):
    """Fava's base exception class."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message
