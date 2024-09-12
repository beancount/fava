"""Template filters for Fava.

All functions in this module will be automatically added as template filters.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING
from unicodedata import normalize

from fava.context import g

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Meta
    from fava.beans.abc import MetaValue


ZERO = Decimal()


def meta_items(meta: Meta | None) -> list[tuple[str, MetaValue]]:
    """Remove keys from a dictionary."""
    if not meta:
        return []
    return [
        (key, value)
        for key, value in meta.items()
        if not (key in {"filename", "lineno"} or key.startswith("__"))
    ]


def format_currency(
    value: Decimal,
    currency: str | None = None,
    *,
    show_if_zero: bool = False,
) -> str:
    """Format a value using the derived precision for a specified currency."""
    if not value and not show_if_zero:
        return ""
    return g.ledger.format_decimal(value or ZERO, currency)


FLAGS_TO_TYPES = {"*": "cleared", "!": "pending"}


def flag_to_type(flag: str) -> str:
    """Names for entry flags."""
    return FLAGS_TO_TYPES.get(flag, "other")


def basename(file_path: str) -> str:
    """Return the basename of a filepath."""
    return normalize("NFC", Path(file_path).name)
