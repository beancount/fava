"""Beancount V2/V3 compatibility."""
# pylint: disable=unused-import
from __future__ import annotations

try:
    from beancount.core.flags import FLAG_UNREALIZED
    from beancount.core.flags import FLAG_RETURNS
except ImportError:  # pragma: no cover
    FLAG_UNREALIZED = "U"
    FLAG_RETURNS = "R"

__all__ = ["FLAG_RETURNS", "FLAG_UNREALIZED"]
