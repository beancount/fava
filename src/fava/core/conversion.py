"""Commodity conversion helpers for Fava.

All functions in this module will be automatically added as template filters.
"""
import datetime
from typing import Any
from typing import Optional
from typing import overload
from typing import Union

from beancount.core.amount import Amount
from beancount.core.convert import convert_position
from beancount.core.convert import get_cost
from beancount.core.convert import get_units
from beancount.core.inventory import Inventory
from beancount.core.position import Position
from beancount.core.prices import get_price
from beancount.core.prices import PriceMap

from fava.core.inventory import CounterInventory
from fava.core.inventory import SimpleCounterInventory


def get_market_value(
    pos: Position, price_map: PriceMap, date: Optional[datetime.date] = None
) -> Amount:
    """Get the market value of a Position.

    This differs from the convert.get_value function in Beancount by returning
    the cost value if no price can be found.

    Args:
        pos: A Position.
        price_map: A dict of prices, as built by prices.build_price_map().
        date: A datetime.date instance to evaluate the value at, or None.

    Returns:
        An Amount, with value converted or if the conversion failed just the
        cost value (or the units if the position has no cost).
    """
    units_ = pos.units
    cost_ = pos.cost
    value_currency = cost_.currency if cost_ else None

    if value_currency:
        base_quote = (units_.currency, value_currency)
        _, price_number = get_price(price_map, base_quote, date)
        assert units_.number is not None
        if price_number is not None:
            return Amount(units_.number * price_number, value_currency)
        return Amount(units_.number * cost_.number, value_currency)
    return units_


@overload
def units(inventory: Inventory) -> Inventory:
    ...


@overload
def units(inventory: CounterInventory) -> SimpleCounterInventory:
    ...


def units(inventory: Union[Inventory, CounterInventory]) -> Any:
    """Get the units of an inventory."""
    return inventory.reduce(get_units)


@overload
def cost(inventory: Inventory) -> Inventory:
    ...


@overload
def cost(inventory: CounterInventory) -> SimpleCounterInventory:
    ...


def cost(inventory: Union[Inventory, CounterInventory]) -> Any:
    """Get the cost of an inventory."""
    return inventory.reduce(get_cost)


@overload
def cost_or_value(
    inventory: Inventory,
    conversion: str,
    price_map: PriceMap,
    date: Optional[datetime.date],
) -> Inventory:
    ...


@overload
def cost_or_value(
    inventory: CounterInventory,
    conversion: str,
    price_map: PriceMap,
    date: Optional[datetime.date],
) -> SimpleCounterInventory:
    ...


def cost_or_value(
    inventory: Union[Inventory, CounterInventory],
    conversion: str,
    price_map: PriceMap,
    date: Optional[datetime.date] = None,
) -> Any:
    """Get the cost or value of an inventory."""
    if conversion == "at_cost":
        return inventory.reduce(get_cost)
    if conversion == "at_value":
        return inventory.reduce(get_market_value, price_map, date)
    if conversion == "units":
        return inventory.reduce(get_units)
    if conversion:
        return inventory.reduce(convert_position, conversion, price_map, date)
    return inventory.reduce(get_cost)
