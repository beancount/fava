"""Typing helpers."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any
from typing import TypedDict

from rustfava.beans.abc import Directive
from rustfava.helpers import BeancountError


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
    account_previous_balances: str
    account_previous_conversions: str
    account_previous_earnings: str
    account_rounding: str | None
    account_unrealized_gains: str

    booking_method: Any  # beancount.core.data.Booking enum
    commodities: set[str]
    conversion_currency: str
    dcontext: Any  # beancount.core.display_context.DisplayContext
    display_precision: dict[str, Decimal]
    documents: Sequence[str]
    include: Sequence[str]
    infer_tolerance_from_cost: bool
    inferred_tolerance_default: dict[str, Decimal]
    inferred_tolerance_multiplier: Decimal
    input_hash: str
    insert_pythonpath: bool
    operating_currency: Sequence[str]
    plugin: Sequence[tuple[str, str | None]]
    plugin_processing_mode: str
    pythonpath: Sequence[str]
    render_commas: bool
    tolerance_multiplier: Decimal

    # deprecated ones
    allow_deprecated_none_for_tags_and_links: bool
    allow_pipe_separator: bool
    long_string_maxlines: int


LoaderResult = tuple[
    Sequence[Directive],
    Sequence[BeancountError],
    BeancountOptions,
]
