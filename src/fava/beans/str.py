"""Convert Beancount types to string."""

from __future__ import annotations

from decimal import Decimal
from functools import singledispatch

from beancount.core.position import CostSpec
from beancount.parser.printer import (  # type: ignore[import-untyped]
    format_entry,
)

from fava.beans.abc import Amount
from fava.beans.abc import Cost
from fava.beans.abc import Directive
from fava.beans.abc import Position
from fava.beans.helpers import replace
from fava.core.misc import align


@singledispatch
def to_string(
    obj: Amount | Cost | CostSpec | Directive | Position,
    _currency_column: int | None = None,
    _indent: int | None = None,
) -> str:
    """Convert to a string."""
    raise TypeError(f"Unsupported object of type {type(obj)}")


@to_string.register(Amount)
def _(obj: Amount) -> str:
    return f"{obj.number} {obj.currency}"


@to_string.register(Cost)
def _(cost: Cost) -> str:
    strs = [f"{cost.number} {cost.currency}"]
    if cost.date:
        strs.append(cost.date.isoformat())
    if cost.label:
        strs.append(f'"{cost.label}"')
    return ", ".join(strs)


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
    units_str = to_string(obj.units)
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
    string = align(format_entry(entry, prefix=" " * indent), currency_column)
    string = string.replace("<class 'beancount.core.number.MISSING'>", "")
    return "\n".join(line.rstrip() for line in string.split("\n"))
