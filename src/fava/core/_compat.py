"""Beancount V2/V3 compatibility."""
# pylint: disable=unused-import

try:
    from beancount.core.flags import FLAG_UNREALIZED
    from beancount.core.flags import FLAG_RETURNS
except ImportError:
    FLAG_UNREALIZED = "U"
    FLAG_RETURNS = "R"

__all__ = ["FLAG_RETURNS", "FLAG_UNREALIZED"]
