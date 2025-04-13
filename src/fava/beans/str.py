"""Convert Beancount types to string."""

from __future__ import annotations

from decimal import Decimal
from functools import singledispatch
from typing import TYPE_CHECKING

from beancount.core import amount
from beancount.core import data
from beancount.core import position
from beancount.core.position import CostSpec
from beancount.parser.printer import format_entry

from fava.beans.abc import Directive
from fava.beans.abc import Position
from fava.beans.helpers import replace
from fava.core.misc import align

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans import protocols


@singledispatch
def to_string(
    obj: amount.Amount
    | protocols.Amount
    | protocols.Cost
    | CostSpec
    | Directive
    | Position,
    _currency_column: int | None = None,
    _indent: int | None = None,
) -> str:
    """Convert to a string."""
    number = getattr(obj, "number", None)
    currency = getattr(obj, "currency", None)
    if isinstance(number, Decimal) and isinstance(currency, str):
        # The Amount and Cost protocols are ambigous, so handle this here
        # instead of having this be dispatched - relevant for older Pythons
        if hasattr(obj, "date"):  # pragma: no cover
            cost_to_string(obj)  # type: ignore[arg-type]
        return f"{number} {currency}"  # pragma: no cover
    msg = f"Unsupported object of type {type(obj)}"
    raise TypeError(msg)


@to_string.register(amount.Amount)
def amount_to_string(obj: amount.Amount | protocols.Amount) -> str:
    """Convert an amount to a string."""
    return f"{obj.number} {obj.currency}"


@to_string.register(position.Cost)
def cost_to_string(cost: protocols.Cost | position.Cost) -> str:
    """Convert a cost to a string."""
    res = f"{cost.number} {cost.currency}, {cost.date.isoformat()}"
    return f'{res}, "{cost.label}"' if cost.label else res


@to_string.register(CostSpec)
def _(cost: CostSpec) -> str:
    strs = []
    if isinstance(cost.number_per, Decimal) or isinstance(
        cost.number_total,
        Decimal,
    ):
        amountlist = []
        if isinstance(cost.number_per, Decimal):
            amountlist.append(f"{cost.number_per}")
        if isinstance(cost.number_total, Decimal):
            amountlist.extend(("#", f"{cost.number_total}"))
        if cost.currency:
            amountlist.append(cost.currency)
        strs.append(" ".join(amountlist))
    if cost.date:
        strs.append(cost.date.isoformat())
    if cost.label:
        strs.append(f'"{cost.label}"')
    if cost.merge:
        strs.append("*")
    return ", ".join(strs)


@to_string.register(Position)
def _(obj: Position) -> str:
    units_str = amount_to_string(obj.units)
    if obj.cost is None:
        return units_str
    cost_str = to_string(obj.cost)
    return f"{units_str} {{{cost_str}}}"


@to_string.register(Directive)
def _format_entry(
    entry: Directive,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    meta = {
        key: entry.meta[key] for key in entry.meta if not key.startswith("_")
    }
    entry = replace(entry, meta=meta)
    assert isinstance(entry, data.ALL_DIRECTIVES)  # noqa: S101
    printed_entry = format_entry(entry, prefix=" " * indent)
    string = align(printed_entry, currency_column)
    string = string.replace("<class 'beancount.core.number.MISSING'>", "")
    return "\n".join(line.rstrip() for line in string.split("\n"))
