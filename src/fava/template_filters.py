"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Callable
from typing import TYPE_CHECKING
from unicodedata import normalize

from fava.beans import funcs
from fava.context import g
from fava.core.conversion import cost_or_value as cost_or_value_without_context
from fava.core.conversion import units

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Meta
    from fava.beans.abc import MetaValue
    from fava.core.inventory import CounterInventory
    from fava.core.inventory import SimpleCounterInventory


ZERO = Decimal()


def meta_items(meta: Meta | None) -> list[tuple[str, MetaValue]]:
    """Remove keys from a dictionary."""
    if not meta:
        return []
    return [
        (key, value)
        for key, value in meta.items()
        if not (key == "filename" or key == "lineno" or key.startswith("__"))
    ]


def cost_or_value(
    inventory: CounterInventory,
    date: datetime.date | None = None,
) -> SimpleCounterInventory:
    """Get the cost or value of an inventory."""
    return cost_or_value_without_context(
        inventory,
        g.conversion,
        g.ledger.prices,
        date,
    )


def format_currency(
    value: Decimal,
    currency: str | None = None,
    show_if_zero: bool = False,
    invert: bool = False,
) -> str:
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ""
    if value == ZERO:
        return g.ledger.format_decimal(ZERO, currency)
    if invert:
        value = -value
    return g.ledger.format_decimal(value, currency)


FLAGS_TO_TYPES = {"*": "cleared", "!": "pending"}


def flag_to_type(flag: str) -> str:
    """Names for entry flags."""
    return FLAGS_TO_TYPES.get(flag, "other")


def basename(file_path: str) -> str:
    """Return the basename of a filepath."""
    return normalize("NFC", Path(file_path).name)


FILTERS: list[
    Callable[
        ...,
        (str | bool | SimpleCounterInventory | list[tuple[str, MetaValue]]),
    ]
] = [
    basename,
    cost_or_value,
    flag_to_type,
    format_currency,
    funcs.hash_entry,
    meta_items,
    units,
]
