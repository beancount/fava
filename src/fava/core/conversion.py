"""Commodity conversion helpers for Fava.

All functions in this module will be automatically added as template filters.
"""
import datetime
from typing import Any
from typing import Optional

from beancount.core.amount import Amount
from beancount.core.convert import convert_position
from beancount.core.convert import get_cost
from beancount.core.convert import get_units
from beancount.core.prices import get_price
from beancount.core.prices import PriceMap


def get_market_value(pos, price_map, date=None):
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
        if price_number is not None:
            return Amount(units_.number * price_number, value_currency)
        return Amount(units_.number * cost_.number, value_currency)
    return units_


def units(inventory):
    """Get the units of an inventory."""
    return inventory.reduce(get_units)


def cost(inventory):
    """Get the cost of an inventory."""
    return inventory.reduce(get_cost)


def cost_or_value(
    inventory,
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
