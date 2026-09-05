"""Alternative implementation of Beancount's Inventory."""

from __future__ import annotations

from decimal import Decimal
from typing import overload
from typing import TYPE_CHECKING

from msgspec import Struct

from fava.beans import protocols
from fava.beans.str import cost_to_string

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Callable
    from collections.abc import Iterator
    from typing import Concatenate
    from typing import ParamSpec

    from beancount.core import amount

    P = ParamSpec("P")


ZERO = Decimal()
InventoryKey = tuple[str, protocols.Cost | None]


class _Amount(Struct, frozen=True):
    number: Decimal
    currency: str

    @overload
    @classmethod
    def from_amount(cls, o: amount.Amount | protocols.Amount) -> _Amount: ...
    @overload
    @classmethod
    def from_amount(cls, o: None) -> None: ...
    @classmethod
    def from_amount(
        cls, o: amount.Amount | protocols.Amount | None
    ) -> _Amount | None:
        return _Amount(o.number, o.currency) if o is not None else None  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]


class _Cost(Struct, frozen=True):
    number: Decimal
    currency: str
    date: datetime.date
    label: str | None

    @overload
    @classmethod
    def from_cost(cls, o: protocols.Cost) -> _Cost: ...
    @overload
    @classmethod
    def from_cost(cls, o: None) -> None: ...
    @classmethod
    def from_cost(cls, o: protocols.Cost | None) -> _Cost | None:
        return (
            _Cost(o.number, o.currency, o.date, o.label)
            if o is not None
            else None
        )


class _Position(Struct, frozen=True):
    units: protocols.Amount
    cost: protocols.Cost | None

    @overload
    @classmethod
    def from_position(cls, p: protocols.Position) -> _Position: ...
    @overload
    @classmethod
    def from_position(cls, p: None) -> None: ...
    @classmethod
    def from_position(cls, p: protocols.Position | None) -> _Position | None:
        return (
            _Position(_Amount.from_amount(p.units), _Cost.from_cost(p.cost))
            if p is not None
            else None
        )


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
        reducer: Callable[
            Concatenate[protocols.Position, P], protocols.Amount
        ],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> SimpleCounterInventory:
        """Reduce inventory."""
        counter = SimpleCounterInventory()
        for currency, number in self.items():
            pos = _Position(_Amount(number, currency), None)
            amount = reducer(pos, *args, **kwargs)
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

    def positions(self) -> Iterator[protocols.Position]:
        """Iterator over the positions in the inventory."""
        for (currency, cost), number in self.items():
            yield _Position(_Amount(number, currency), cost)

    def reduce(
        self,
        reducer: Callable[
            Concatenate[protocols.Position, P], protocols.Amount
        ],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> SimpleCounterInventory:
        """Reduce inventory.

        Note that this returns a simple :class:`CounterInventory` with just
        currencies as keys.
        """
        counter = SimpleCounterInventory()
        for pos in self.positions():
            amount = reducer(pos, *args, **kwargs)
            counter.add(amount.currency, amount.number)
        return counter

    def add_amount(
        self, amount: protocols.Amount, cost: protocols.Cost | None = None
    ) -> None:
        """Add an Amount to the inventory."""
        key = (amount.currency, cost)
        self.add(key, amount.number)

    def add_position(self, pos: protocols.Position) -> None:
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
