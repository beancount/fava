"""Load Beancount files and strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beancount.loader import load_string as load_string_bc

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.types import LoaderResult


def load_string(value: str) -> LoaderResult:
    """Load a Beancoun string."""
    return load_string_bc(value)
