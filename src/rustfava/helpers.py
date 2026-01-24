"""Exceptions and module base class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.beans.abc import Directive
    from rustfava.beans.abc import Meta


@dataclass(frozen=True, slots=True)
class BeancountError:
    """Dataclass for a Beancount-style error."""

    source: Meta | None
    message: str
    entry: Directive | None


class RustfavaAPIError(Exception):
    """Fava's base exception class."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message
