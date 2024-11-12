"""Various functions to deal with Beancount data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beancount.core import compare  # type: ignore[attr-defined]

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def hash_entry(entry: Directive) -> str:
    """Hash an entry."""
    if hasattr(entry, "_fields"):
        return compare.hash_entry(entry)  # type: ignore[no-any-return]
    return str(hash(entry))


def get_position(entry: Directive) -> tuple[str, int]:
    """Get the filename and position from the entry metadata."""
    meta = entry.meta
    filename = meta["filename"]
    lineno = meta["lineno"]
    if isinstance(filename, str) and isinstance(lineno, int):
        return (filename, lineno)
    msg = "Invalid filename or lineno in entry metadata."
    raise ValueError(msg)
