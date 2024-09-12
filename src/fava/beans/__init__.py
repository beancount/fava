"""Types, functions and wrappers to deal with Beancount types."""

from __future__ import annotations

try:  # pragma: no cover
    from beancount import query  # noqa: F401

    BEANCOUNT_V3 = False
except ImportError:
    BEANCOUNT_V3 = True
