"""Exceptions and module base class."""

from __future__ import annotations

from typing import NamedTuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.beans.abc import Meta


class BeancountError(NamedTuple):
    """NamedTuple base for a Beancount-style error."""

    source: Meta | None
    message: str
    entry: Directive | None = None


class FavaAPIError(Exception):
    """Fava's base exception class."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__()
        self.message = message if message is not None else self.__doc__ or ""

    def __str__(self) -> str:
        return self.message
