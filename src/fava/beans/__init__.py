"""Types, functions and wrappers to deal with Beancount types."""

from __future__ import annotations

from beancount import __version__

BEANCOUNT_V3 = not __version__.startswith("2")
