"""Various functions to deal with Beancount data."""

from __future__ import annotations

import hashlib
from typing import Any
from typing import TYPE_CHECKING

from beancount.core import compare

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def _hash_value(value: Any) -> str:
    """Convert a value to a hashable string representation."""
    if value is None:
        return "None"
    if isinstance(value, (str, int, float, bool)):
        return repr(value)
    if isinstance(value, dict):
        items = sorted((k, _hash_value(v)) for k, v in value.items())
        return "{" + ",".join(f"{k}:{v}" for k, v in items) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_hash_value(v) for v in value) + "]"
    if hasattr(value, "__dict__"):
        # For objects like RLAmount, RLCost, etc.
        items = sorted((k, _hash_value(v)) for k, v in value.__dict__.items())
        return type(value).__name__ + "{" + ",".join(f"{k}:{v}" for k, v in items) + "}"
    return repr(value)


def _hash_rl_entry(entry: Directive) -> str:
    """Hash a rustledger entry using its fields."""
    parts = [type(entry).__name__]
    if hasattr(entry, "__dataclass_fields__"):
        for field_name in entry.__dataclass_fields__:
            value = getattr(entry, field_name)
            parts.append(f"{field_name}={_hash_value(value)}")
    else:
        # Fallback for non-dataclass objects
        parts.append(_hash_value(entry.__dict__))

    content = "|".join(parts)
    return hashlib.md5(content.encode()).hexdigest()


def hash_entry(entry: Directive) -> str:
    """Hash an entry."""
    if hasattr(entry, "_fields"):
        # Beancount named tuple
        return compare.hash_entry(entry)  # type: ignore[arg-type]
    if hasattr(entry, "__dataclass_fields__"):
        # Rustledger dataclass
        return _hash_rl_entry(entry)
    # Fallback for other types (strings, etc.) - use built-in hash
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
