"""Typing helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict

    from beancount.core.display_context import DisplayContext

    from fava.beans.abc import Directive
    from fava.helpers import BeancountError

    class BeancountOptions(TypedDict):
        """Beancount options."""

        title: str
        filename: str
        name_assets: str
        name_liabilities: str
        name_equity: str
        name_income: str
        name_expenses: str
        account_current_conversions: str
        account_current_earnings: str
        render_commas: bool
        operating_currency: list[str]
        documents: list[str]
        include: list[str]
        dcontext: DisplayContext

    LoaderResult = tuple[
        list[Directive],
        list[BeancountError],
        BeancountOptions,
    ]
