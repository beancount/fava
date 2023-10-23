"""Alternative implementation of Beancount's Inventory."""

from __future__ import annotations

from decimal import Decimal
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

from fava.beans import create
from fava.beans.abc import Cost

if TYPE_CHECKING:  # pragma: no cover
    from typing import Concatenate
    from typing import Iterable
    from typing import Iterator
    from typing import ParamSpec

    from fava.beans.abc import Amount
    from fava.beans.abc import Position

    P = ParamSpec("P")


ZERO = Decimal()
InventoryKey = Tuple[str, Optional[Cost]]


class SimpleCounterInventory(Dict[str, Decimal]):
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


class CounterInventory(Dict[InventoryKey, Decimal]):
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

    @staticmethod
    def from_positions(positions: Iterable[Position]) -> CounterInventory:
        inv = CounterInventory()
        for position in positions:
            inv.add_position(position)
        return inv

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
            pos = create.position(create.amount((number, currency)), cost)
            amount = reducer(pos, *args)
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
