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


class CostSpec(Protocol):
    """A cost specification (uses number_per/number_total instead of number)."""

    @property
    def number_per(self) -> Decimal | None:
        """Per-unit cost."""

    @property
    def number_total(self) -> Decimal | None:
        """Total cost."""

    @property
    def currency(self) -> str | None:
        """Currency of the cost."""

    @property
    def date(self) -> datetime.date | None:
        """Date of the cost."""

    @property
    def label(self) -> str | None:
        """Label of the cost."""

    @property
    def merge(self) -> bool | None:
        """Whether to merge lots."""


class Position(Protocol):
    """A Beancount position - just cost and units."""

    @property
    def units(self) -> Amount:
        """Units of the posting."""

    @property
    def cost(self) -> Cost | None:
        """Units of the position."""
