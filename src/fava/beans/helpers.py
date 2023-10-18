"""Helpers for Beancount entries."""

from __future__ import annotations

from typing import Any
from typing import TypeVar

from fava.beans.abc import Directive
from fava.beans.abc import Posting

T = TypeVar("T", Directive, Posting)


def replace(entry: T, **kwargs: Any) -> T:
    """Create a copy of the given directive, replacing some arguments."""
    if isinstance(entry, tuple):
        return entry._replace(**kwargs)  # type: ignore[attr-defined,no-any-return]
    raise TypeError(f"Could not replace attribute in type {type(entry)}")
