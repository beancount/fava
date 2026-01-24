"""Various functions to deal with Beancount data."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def hash_entry(entry: Directive) -> str:
    """Hash an entry."""
    # Rustledger provides pre-computed hash in meta
    meta = getattr(entry, "meta", None)
    if meta and isinstance(meta, dict) and "hash" in meta:
        return meta["hash"]
    # Rustledger dataclass (for plugin-generated entries without hash)
    if hasattr(entry, "__dataclass_fields__"):
        content = f"{type(entry).__name__}|{entry.date}|{getattr(entry, 'account', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    # Beancount namedtuple (for entries created by create module)
    if hasattr(entry, "_fields"):
        content = f"{type(entry).__name__}|{entry.date}|{getattr(entry, 'narration', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    # Fallback for other types
    return hashlib.md5(str(entry).encode()).hexdigest()


def get_position(entry: Directive) -> tuple[str, int]:
    """Get the filename and position from the entry metadata."""
    meta = entry.meta
    filename = meta["filename"]
    lineno = meta["lineno"]
    if isinstance(filename, str) and isinstance(lineno, int):
        return (filename, lineno)
    msg = "Invalid filename or lineno in entry metadata."
    raise ValueError(msg)
