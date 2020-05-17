"""Alternative implementation of Beancount's Inventory."""
from typing import Dict
from typing import Optional
from typing import Tuple

from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.number import ZERO
from beancount.core.position import Position


InventoryKey = Tuple[str, Optional[str]]


class CounterInventory(Dict[InventoryKey, Decimal]):
    """A lightweight inventory.

    This is intended as a faster alternative to Beancount's Inventory class.
    Due to not using a list, for inventories with a lot of different positions,
    inserting is much faster.

    The keys should be tuples ``(currency, cost)``.
    """

    # False positive due to use of the typing.Dict base instead of dict
    # pylint: disable=no-member,unsupported-assignment-operation

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

    def reduce(self, reducer, *args) -> "CounterInventory":
        """Reduce inventory.

        Note that this returns a simple :class:`CounterInventory` with just
        currencies as keys.
        """
        counter = CounterInventory()
        for (currency, cost), number in self.items():
            pos = Position(Amount(number, currency), cost)
            amount = reducer(pos, *args)
            counter.add(amount.currency, amount.number)
        return counter

    def add_amount(self, amount, cost=None):
        """Add an Amount to the inventory."""
        key = (amount.currency, cost)
        self.add(key, amount.number)

    def add_position(self, pos):
        """Add a Position or Posting to the inventory."""
        self.add_amount(pos.units, pos.cost)

    def __neg__(self) -> "CounterInventory":
        return CounterInventory({key: -num for key, num in self.items()})

    def __add__(self, other) -> "CounterInventory":
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
