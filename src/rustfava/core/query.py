"""Query result types."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from rustfava.rustledger.types import RLAmount
from rustfava.rustledger.types import RLPosition
from rustfava.core.conversion import UNITS

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any
    from typing import Literal
    from typing import TypeAlias
    from typing import TypeVar

    from rustfava.core.inventory import SimpleCounterInventory

    T = TypeVar("T")

    QueryRowValue = Any

    # This is not a complete enumeration of all possible column types but just
    # of the ones we pass in some specific serialisation to the frontend.
    # Everything unknown will be stringified (by ObjectColumn).
    SerialisedQueryRowValue = (
        bool
        | int
        | str
        | datetime.date
        | Decimal
        | RLPosition
        | SimpleCounterInventory
        | None
    )


@dataclass(frozen=True)
class QueryResultTable:
    """Table query result."""

    types: list[BaseColumn]
    rows: list[tuple[SerialisedQueryRowValue, ...]]
    t: Literal["table"] = "table"


@dataclass(frozen=True)
class QueryResultText:
    """Text query result."""

    contents: str
    t: Literal["string"] = "string"


QueryResult: TypeAlias = QueryResultTable | QueryResultText


@dataclass(frozen=True)
class BaseColumn:
    """A query column."""

    name: str
    dtype: str

    @staticmethod
    def serialise(
        val: QueryRowValue,
    ) -> SerialisedQueryRowValue:
        """Serialiseable version of the column value."""
        return val  # type: ignore[no-any-return]


@dataclass(frozen=True)
class BoolColumn(BaseColumn):
    """A boolean query column."""

    dtype: str = "bool"


@dataclass(frozen=True)
class DecimalColumn(BaseColumn):
    """A Decimal query column."""

    dtype: str = "Decimal"


@dataclass(frozen=True)
class IntColumn(BaseColumn):
    """A int query column."""

    dtype: str = "int"


@dataclass(frozen=True)
class StrColumn(BaseColumn):
    """A str query column."""

    dtype: str = "str"


@dataclass(frozen=True)
class DateColumn(BaseColumn):
    """A date query column."""

    dtype: str = "date"


@dataclass(frozen=True)
class PositionColumn(BaseColumn):
    """A Position query column."""

    dtype: str = "Position"


@dataclass(frozen=True)
class SetColumn(BaseColumn):
    """A set query column."""

    dtype: str = "set"


@dataclass(frozen=True)
class AmountColumn(BaseColumn):
    """An amount query column."""

    dtype: str = "Amount"


@dataclass(frozen=True)
class ObjectColumn(BaseColumn):
    """An object query column."""

    dtype: str = "object"

    @staticmethod
    def serialise(val: object) -> str:
        """Serialise an object of unknown type to a string."""
        return str(val)


@dataclass(frozen=True)
class InventoryColumn(BaseColumn):
    """An inventory query column."""

    dtype: str = "Inventory"

    @staticmethod
    def serialise(
        val: dict[str, Decimal] | None,
    ) -> SimpleCounterInventory | None:
        """Serialise an inventory.

        Rustledger returns inventory as a dict of currency -> Decimal.
        """
        if val is None:
            return None
        # Rustledger already converts to {currency: Decimal} format
        if isinstance(val, dict):
            from rustfava.core.inventory import SimpleCounterInventory
            return SimpleCounterInventory(val)
        # Fallback for beancount Inventory type (for backwards compat)
        return UNITS.apply_inventory(val) if val is not None else None


COLUMNS = {
    RLAmount: AmountColumn,
    Decimal: DecimalColumn,
    dict: InventoryColumn,  # Rustledger returns inventory as dict
    RLPosition: PositionColumn,
    object: ObjectColumn,  # Fallback for Position from rustledger
    bool: BoolColumn,
    datetime.date: DateColumn,
    int: IntColumn,
    set: SetColumn,
    frozenset: SetColumn,  # Rustledger returns frozenset for sets
    str: StrColumn,
}
