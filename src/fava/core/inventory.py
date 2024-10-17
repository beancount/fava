"""Alternative implementation of Beancount's Inventory."""

from __future__ import annotations

from decimal import Decimal
from typing import Callable
from typing import NamedTuple
from typing import Optional
from typing import TYPE_CHECKING

from fava.beans.protocols import Cost
from fava.beans.str import cost_to_string

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Iterator
    from typing import Concatenate
    from typing import ParamSpec

    from fava.beans.protocols import Amount
    from fava.beans.protocols import Position

    P = ParamSpec("P")


ZERO = Decimal()
InventoryKey = tuple[str, Optional[Cost]]


class _Amount(NamedTuple):
    number: Decimal
    currency: str


class _Cost(NamedTuple):
    number: Decimal
    currency: str
    date: datetime.date
    label: str | None


class _Position(NamedTuple):
    units: Amount
    cost: Cost | None


class SimpleCounterInventory(dict[str, Decimal]):
    """A simple inventory mapping just strings to numbers."""

    def is_empty(self) -> bool:
        """Check if the inventory is empty."""
        return not bool(self)

    def add(self, key: str, number: Decimal) -> None:
        """Add a number to key."""
        new_num = number + self.get(key, ZERO)
        if new_num == ZERO:
            self.pop(key, None)
        else:
            self[key] = new_num

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError

    def __neg__(self) -> SimpleCounterInventory:
        return SimpleCounterInventory({key: -num for key, num in self.items()})

    def reduce(
        self,
        reducer: Callable[Concatenate[Position, P], Amount],
        *args: P.args,
        **_kwargs: P.kwargs,
    ) -> SimpleCounterInventory:
        """Reduce inventory."""
        counter = SimpleCounterInventory()
        for currency, number in self.items():
            pos = _Position(_Amount(number, currency), None)
            amount = reducer(pos, *args)  # type: ignore[call-arg]
            counter.add(amount.currency, amount.number)
        return counter


class CounterInventory(dict[InventoryKey, Decimal]):
    """A lightweight inventory.

    This is intended as a faster alternative to Beancount's Inventory class.
    Due to not using a list, for inventories with a lot of different positions,
    inserting is much faster.

    The keys should be tuples ``(currency, cost)``.
    """

    def is_empty(self) -> bool:
        """Check if the inventory is empty."""
        return not bool(self)

    def add(self, key: InventoryKey, number: Decimal) -> None:
        """Add a number to key."""
        new_num = number + self.get(key, ZERO)
        if new_num == ZERO:
            self.pop(key, None)
        else:
            self[key] = new_num

    def __iter__(self) -> Iterator[InventoryKey]:
        raise NotImplementedError

    def to_strings(self) -> list[str]:
        """Print as a list of strings (e.g. for snapshot tests)."""
        strings = []
        for (currency, cost), number in self.items():
            if cost is None:
                strings.append(f"{number} {currency}")
            else:
                cost_str = cost_to_string(cost)
                strings.append(f"{number} {currency} {{{cost_str}}}")
        return strings

    def reduce(
        self,
        reducer: Callable[Concatenate[Position, P], Amount],
        *args: P.args,
        **_kwargs: P.kwargs,
    ) -> SimpleCounterInventory:
        """Reduce inventory.

        Note that this returns a simple :class:`CounterInventory` with just
        currencies as keys.
        """
        counter = SimpleCounterInventory()
        for (currency, cost), number in self.items():
            pos = _Position(_Amount(number, currency), cost)
            amount = reducer(pos, *args)  # type: ignore[call-arg]
            counter.add(amount.currency, amount.number)
        return counter

    def add_amount(self, amount: Amount, cost: Cost | None = None) -> None:
        """Add an Amount to the inventory."""
        key = (amount.currency, cost)
        self.add(key, amount.number)

    def add_position(self, pos: Position) -> None:
        """Add a Position or Posting to the inventory."""
        self.add_amount(pos.units, pos.cost)

    def __neg__(self) -> CounterInventory:
        return CounterInventory({key: -num for key, num in self.items()})

    def __add__(self, other: CounterInventory) -> CounterInventory:
        counter = CounterInventory(self)
        counter.add_inventory(other)
        return counter

    def add_inventory(self, counter: CounterInventory) -> None:
        """Add another :class:`CounterInventory`."""
        if not self:
            self.update(counter)
        else:
            self_get = self.get
            for key, num in counter.items():
                new_num = num + self_get(key, ZERO)
                if new_num == ZERO:
                    self.pop(key, None)
                else:
                    self[key] = new_num
