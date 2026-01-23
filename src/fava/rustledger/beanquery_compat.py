"""Compatibility layer for beanquery.

beanquery uses isinstance checks against beancount.core.data types,
so we need to convert our RL* types to beancount types when running queries.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from beancount.core import amount as bc_amount
from beancount.core import data
from beancount.core import position

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from fava.beans.abc import Directive


def _convert_amount(
    rl_amount: Any,
) -> bc_amount.Amount | None:
    """Convert RLAmount to beancount Amount."""
    if rl_amount is None:
        return None
    return bc_amount.Amount(rl_amount.number, rl_amount.currency)


def _convert_cost(rl_cost: Any) -> position.Cost | None:
    """Convert RLCost to beancount Cost."""
    if rl_cost is None:
        return None
    return position.Cost(
        rl_cost.number,
        rl_cost.currency,
        rl_cost.date,
        rl_cost.label,
    )


def _convert_posting(rl_posting: Any) -> data.Posting:
    """Convert RLPosting to beancount Posting."""
    return data.Posting(
        rl_posting.account,
        _convert_amount(rl_posting.units),
        _convert_cost(rl_posting.cost),
        _convert_amount(rl_posting.price),
        rl_posting.flag,
        dict(rl_posting.meta) if rl_posting.meta else {},
    )


def _convert_meta(meta: Any) -> dict[str, Any]:
    """Convert meta to a regular dict."""
    if meta is None:
        return {}
    return dict(meta)


def to_beancount_entry(entry: Directive) -> data.Directive | None:
    """Convert a rustledger entry to a beancount entry.

    Returns None if the entry type is not supported by beancount.
    """
    entry_type = type(entry).__name__

    if entry_type == "RLTransaction":
        return data.Transaction(
            _convert_meta(entry.meta),
            entry.date,
            entry.flag,
            entry.payee,
            entry.narration,
            entry.tags,
            entry.links,
            [_convert_posting(p) for p in entry.postings],
        )

    if entry_type == "RLBalance":
        return data.Balance(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
            _convert_amount(entry.amount),
            entry.tolerance,
            entry.diff_amount,
        )

    if entry_type == "RLOpen":
        return data.Open(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
            list(entry.currencies) if entry.currencies else None,
            None,  # booking - beancount uses Booking enum
        )

    if entry_type == "RLClose":
        return data.Close(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
        )

    if entry_type == "RLPrice":
        return data.Price(
            _convert_meta(entry.meta),
            entry.date,
            entry.currency,
            _convert_amount(entry.amount),
        )

    if entry_type == "RLNote":
        return data.Note(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
            entry.comment,
            entry.tags,
            entry.links,
        )

    if entry_type == "RLEvent":
        return data.Event(
            _convert_meta(entry.meta),
            entry.date,
            entry.type,
            entry.description,
        )

    if entry_type == "RLPad":
        return data.Pad(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
            entry.source_account,
        )

    if entry_type == "RLDocument":
        return data.Document(
            _convert_meta(entry.meta),
            entry.date,
            entry.account,
            entry.filename,
            entry.tags,
            entry.links,
        )

    if entry_type == "RLCommodity":
        return data.Commodity(
            _convert_meta(entry.meta),
            entry.date,
            entry.currency,
        )

    if entry_type == "RLQuery":
        return data.Query(
            _convert_meta(entry.meta),
            entry.date,
            entry.name,
            entry.query_string,
        )

    if entry_type == "RLCustom":
        # Custom values need special handling
        values = []
        for v in entry.values:
            # beanquery expects the raw value, not wrapped
            values.append(v.value)
        return data.Custom(
            _convert_meta(entry.meta),
            entry.date,
            entry.type,
            values,
        )

    # Already a beancount type
    if isinstance(entry, data.ALL_DIRECTIVES):
        return entry

    return None


def to_beancount_entries(
    entries: Sequence[Directive],
) -> list[data.Directive]:
    """Convert a sequence of entries to beancount entries.

    Filters out entries that cannot be converted.
    """
    result = []
    for entry in entries:
        bc_entry = to_beancount_entry(entry)
        if bc_entry is not None:
            result.append(bc_entry)
    return result
