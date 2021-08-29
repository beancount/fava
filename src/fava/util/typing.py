"""Typing helpers."""
from typing import List

from beancount.core.display_context import DisplayContext

try:
    from typing_extensions import TypedDict  # below Python 3.8
except ImportError:
    from typing import TypedDict


class BeancountOptions(TypedDict):
    """Beancount options."""

    title: str
    name_assets: str
    name_liabilities: str
    name_equity: str
    name_income: str
    name_expenses: str
    account_current_conversions: str
    account_current_earnings: str
    render_commas: bool
    operating_currency: List[str]
    documents: List[str]
    include: List[str]
    dcontext: DisplayContext


__all__ = ["BeancountOptions", "TypedDict"]
