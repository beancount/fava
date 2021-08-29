"""Alternative implementation of Beancount's Inventory."""
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple

from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.number import ZERO
from beancount.core.position import Cost
from beancount.core.position import Position


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

    def reduce(
        self, reducer: Callable[..., Amount], *args: Any
    ) -> SimpleCounterInventory:
        """Reduce inventory.

        Note that this returns a simple :class:`CounterInventory` with just
        currencies as keys.
        """
        counter = SimpleCounterInventory()
        for (currency, cost), number in self.items():
            pos = Position(Amount(number, currency), cost)
            amount = reducer(pos, *args)
            assert amount.number is not None
            counter.add(amount.currency, amount.number)
        return counter

    def add_amount(self, amount: Amount, cost: Optional[Cost] = None) -> None:
        """Add an Amount to the inventory."""
        assert amount.number is not None
        key = (amount.currency, cost)
        self.add(key, amount.number)

    def add_position(self, pos: Position) -> None:
        """Add a Position or Posting to the inventory."""
        self.add_amount(pos.units, pos.cost)

    def __neg__(self) -> "CounterInventory":
        return CounterInventory({key: -num for key, num in self.items()})

    def __add__(self, other: "CounterInventory") -> "CounterInventory":
        counter = CounterInventory(self)
        counter.add_inventory(other)
        return counter

    def add_inventory(self, counter: "CounterInventory") -> None:
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
