"""Utils for Python sets."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Set as AbstractSet


def add_to_set(set_: AbstractSet[str] | None, new: str) -> set[str]:
    """Add an entry to a set (or create it if doesn't exist).

    Args:
        set_: The (optional) set to add an element to.
        new: The string to add to the set.
    """
    return set(set_).union([new]) if set_ is not None else {new}
