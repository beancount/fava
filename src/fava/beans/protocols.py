"""Abstract base classes for Beancount types."""

from __future__ import annotations

from typing import Protocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from decimal import Decimal


class Amount(Protocol):
    """An amount in some currency."""

    @property
    def number(self) -> Decimal:
        """Number of units in the amount."""

    @property
    def currency(self) -> str:
        """Currency of the amount."""


class Cost(Protocol):
    """A cost (basically an amount with date and label)."""

    @property
    def number(self) -> Decimal:
        """Number of units in the cost."""

    @property
    def currency(self) -> str:
        """Currency of the cost."""

    @property
    def date(self) -> datetime.date:
        """Date of the cost."""

    @property
    def label(self) -> str | None:
        """Label of the cost."""


class Position(Protocol):
    """A Beancount position - just cost and units."""

    @property
    def units(self) -> Amount:
        """Units of the posting."""

    @property
    def cost(self) -> Cost | None:
        """Units of the position."""
