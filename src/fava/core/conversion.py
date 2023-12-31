"""Commodity conversion helpers for Fava.

All functions in this module will be automatically added as template filters.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from fava.core.inventory import _Amount
from fava.core.inventory import SimpleCounterInventory

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from beancount.core.inventory import Inventory

    from fava.beans.prices import FavaPriceMap
    from fava.beans.protocols import Amount
    from fava.beans.protocols import Position
    from fava.core.inventory import CounterInventory


def get_units(pos: Position) -> Amount:
    """Return the units of a Position."""
    return pos.units


def get_cost(pos: Position) -> Amount:
    """Return the total cost of a Position."""
    cost_ = pos.cost
    return (
        _Amount(cost_.number * pos.units.number, cost_.currency)
        if cost_ is not None
        else pos.units
    )


def get_market_value(
    pos: Position,
    prices: FavaPriceMap,
    date: datetime.date | None = None,
) -> Amount:
    """Get the market value of a Position.

    This differs from the convert.get_value function in Beancount by returning
    the cost value if no price can be found.

    Args:
        pos: A Position.
        prices: A FavaPriceMap
        date: A datetime.date instance to evaluate the value at, or None.

    Returns:
        An Amount, with value converted or if the conversion failed just the
        cost value (or the units if the position has no cost).
    """
    units_ = pos.units
    cost_ = pos.cost

    if cost_ is not None:
        value_currency = cost_.currency
        base_quote = (units_.currency, value_currency)
        price_number = prices.get_price(base_quote, date)
        if price_number is not None:
            return _Amount(
                units_.number * price_number,
                value_currency,
            )
        return _Amount(units_.number * cost_.number, value_currency)
    return units_


def convert_position(
    pos: Position,
    target_currency: str,
    prices: FavaPriceMap,
    date: datetime.date | None = None,
) -> Amount:
    """Get the value of a Position in a particular currency.

    Args:
        pos: A Position.
        target_currency: The target currency to convert to.
        prices: A FavaPriceMap
        date: A datetime.date instance to evaluate the value at, or None.

    Returns:
        An Amount, with value converted or if the conversion failed just the
        cost value (or the units if the position has no cost).
    """
    units_ = pos.units

    # try the direct conversion
    base_quote = (units_.currency, target_currency)
    price_number = prices.get_price(base_quote, date)
    if price_number is not None:
        return _Amount(units_.number * price_number, target_currency)

    cost_ = pos.cost
    if cost_ is not None:
        cost_currency = cost_.currency
        if cost_currency != target_currency:
            base_quote1 = (units_.currency, cost_currency)
            rate1 = prices.get_price(base_quote1, date)
            if rate1 is not None:
                base_quote2 = (cost_currency, target_currency)
                rate2 = prices.get_price(base_quote2, date)
                if rate2 is not None:
                    return _Amount(
                        units_.number * rate1 * rate2,
                        target_currency,
                    )
    return units_


def simple_units(
    inventory: Inventory,
) -> SimpleCounterInventory:
    """Get the units of an inventory."""
    res = SimpleCounterInventory()
    for pos in inventory:
        res.add(pos.units.currency, pos.units.number)
    return res


def units(
    inventory: CounterInventory,
) -> SimpleCounterInventory:
    """Get the units of an inventory."""
    return inventory.reduce(get_units)


class Conversion(ABC):
    """A conversion."""

    @abstractmethod
    def apply(
        self,
        inventory: CounterInventory,
        prices: FavaPriceMap,
        date: datetime.date | None = None,
    ) -> SimpleCounterInventory:
        """Apply the conversion to an inventory."""


class _AtCostConversion(Conversion):
    def apply(
        self,
        inventory: CounterInventory,
        prices: FavaPriceMap,  # noqa: ARG002
        date: datetime.date | None = None,  # noqa: ARG002
    ) -> SimpleCounterInventory:
        return inventory.reduce(get_cost)


class _AtValueConversion(Conversion):
    def apply(
        self,
        inventory: CounterInventory,
        prices: FavaPriceMap,
        date: datetime.date | None = None,
    ) -> SimpleCounterInventory:
        return inventory.reduce(get_market_value, prices, date)


class _UnitsConversion(Conversion):
    def apply(
        self,
        inventory: CounterInventory,
        prices: FavaPriceMap,  # noqa: ARG002
        date: datetime.date | None = None,  # noqa: ARG002
    ) -> SimpleCounterInventory:
        return inventory.reduce(get_units)


class _CurrencyConversion(Conversion):
    """Conversion to a list of currencies."""

    def __init__(self, value: str) -> None:
        self._currencies = tuple(value.split(","))

    def apply(
        self,
        inventory: CounterInventory,
        prices: FavaPriceMap,
        date: datetime.date | None = None,
    ) -> SimpleCounterInventory:
        currencies = iter(self._currencies)
        currency = next(currencies)
        res = inventory.reduce(convert_position, currency, prices, date)
        for currency in currencies:
            res = res.reduce(convert_position, currency, prices, date)
        return res


#: Convert position to its total cost.
AT_COST = _AtCostConversion()
#: Convert position to its market value.
AT_VALUE = _AtValueConversion()
#: Convert position to its units.
UNITS = _UnitsConversion()


def conversion_from_str(value: str) -> Conversion:
    """Parse a conversion string."""
    if value == "at_cost":
        return AT_COST
    if value == "at_value":
        return AT_VALUE
    if value == "units":
        return UNITS

    return _CurrencyConversion(value)


def cost_or_value(
    inventory: CounterInventory,
    conversion: str | Conversion,
    prices: FavaPriceMap,
    date: datetime.date | None = None,
) -> SimpleCounterInventory:
    """Get the cost or value of an inventory."""
    if isinstance(conversion, str):
        conversion = conversion_from_str(conversion)

    return conversion.apply(inventory, prices, date)
