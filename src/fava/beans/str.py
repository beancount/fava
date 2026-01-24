"""Convert Beancount types to string."""

from __future__ import annotations

import io
import re
from decimal import Decimal
from functools import singledispatch
from typing import TYPE_CHECKING

from fava.beans.abc import Balance
from fava.beans.abc import Close
from fava.beans.abc import Commodity
from fava.beans.abc import Custom
from fava.beans.abc import Directive
from fava.beans.abc import Document
from fava.beans.abc import Event
from fava.beans.abc import Note
from fava.beans.abc import Open
from fava.beans.abc import Pad
from fava.beans.abc import Position
from fava.beans.abc import Posting
from fava.beans.abc import Price
from fava.beans.abc import Query
from fava.beans.abc import Transaction


# Currency alignment regex (moved here from core.misc to avoid circular import)
CURRENCY_RE = r"[A-Z][A-Z0-9\'\.\_\-]{0,22}[A-Z0-9]"
ALIGN_RE = re.compile(
    rf'([^";]*?)\s+([-+]?\s*[\d,]+(?:\.\d*)?)\s+({CURRENCY_RE}\b.*)',
)


def align(string: str, currency_column: int) -> str:
    """Align currencies in one column."""
    output = io.StringIO()
    for line in string.splitlines():
        match = ALIGN_RE.match(line)
        if match:
            prefix, number, rest = match.groups()
            num_of_spaces = currency_column - len(prefix) - len(number) - 4
            spaces = " " * num_of_spaces
            output.write(prefix + spaces + "  " + number + " " + rest)
        else:
            output.write(line)
        output.write("\n")

    return output.getvalue()

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans import protocols


@singledispatch
def to_string(
    obj: protocols.Amount
    | protocols.Cost
    | Directive
    | Position
    | Posting,
    _currency_column: int | None = None,
    _indent: int | None = None,
) -> str:
    """Convert to a string."""
    # Check if it's a CostSpec (has number_per attribute)
    if hasattr(obj, "number_per"):
        return costspec_to_string(obj)

    number = getattr(obj, "number", None)
    currency = getattr(obj, "currency", None)
    if isinstance(number, Decimal) and isinstance(currency, str):
        # The Amount and Cost protocols are ambiguous, so handle this here
        # instead of having this be dispatched - relevant for older Pythons
        if hasattr(obj, "date"):
            return cost_to_string(obj)  # type: ignore[arg-type]
        return f"{number} {currency}"
    msg = f"Unsupported object of type {type(obj)}"
    raise TypeError(msg)


def amount_to_string(obj: protocols.Amount) -> str:
    """Convert an amount to a string."""
    return f"{obj.number} {obj.currency}"


def cost_to_string(cost: protocols.Cost) -> str:
    """Convert a cost to a string."""
    parts = [f"{cost.number} {cost.currency}"]
    if cost.date is not None:
        parts.append(cost.date.isoformat())
    if cost.label:
        parts.append(f'"{cost.label}"')
    return ", ".join(parts)


@to_string.register(Position)
def _position_to_string(obj: Position) -> str:
    units_str = amount_to_string(obj.units)
    if obj.cost is None:
        return units_str
    cost_str = cost_to_string(obj.cost)
    return f"{units_str} {{{cost_str}}}"


def costspec_to_string(cost: object) -> str:
    """Convert a CostSpec to a string.

    CostSpec has number_per/number_total instead of number, and may use MISSING.
    """
    # Handle MISSING sentinel - it's a class used as a sentinel value
    def is_missing(val: object) -> bool:
        if val is None:
            return False
        # MISSING is a class used as a sentinel in beancount
        # When used in CostSpec, the actual class is stored, not an instance
        # So we check if val is a class AND its name is MISSING
        if isinstance(val, type) and val.__name__ == "MISSING":
            return True
        # Also handle instances of MISSING-like classes
        if type(val).__name__ == "MISSING":
            return True
        return False

    number_per = getattr(cost, "number_per", None)
    number_total = getattr(cost, "number_total", None)
    currency = getattr(cost, "currency", None)
    date = getattr(cost, "date", None)
    label = getattr(cost, "label", None)
    merge = getattr(cost, "merge", None)

    # If all values are MISSING, None, or False, return empty
    all_none = (
        (number_per is None or is_missing(number_per))
        and (number_total is None or is_missing(number_total))
        and (currency is None or is_missing(currency))
        and date is None
        and not label
        and not merge
    )
    if all_none:
        return ""

    parts = []

    # Build the amount part: "number_per # number_total currency"
    amount_parts = []
    if number_per is not None and not is_missing(number_per):
        amount_parts.append(str(number_per))
    if number_total is not None and not is_missing(number_total):
        amount_parts.extend(["#", str(number_total)])
    if currency is not None and not is_missing(currency) and isinstance(currency, str):
        amount_parts.append(currency)
    if amount_parts:
        parts.append(" ".join(amount_parts))

    if date is not None:
        parts.append(date.isoformat())
    if label:
        parts.append(f'"{label}"')
    if merge:
        parts.append("*")

    return ", ".join(parts)


@to_string.register(Posting)
def _posting_to_string(posting: Posting) -> str:
    """Convert a posting to a string (units + cost, not price).

    Note: Price is NOT included here - it's added by serialise(Posting)
    in serialisation.py when needed.
    """
    if posting.units is None:
        return ""
    units_str = amount_to_string(posting.units)
    if posting.cost is None:
        return units_str

    # Check if it's a CostSpec (has number_per) or Cost (has number)
    if hasattr(posting.cost, "number_per"):
        cost_str = costspec_to_string(posting.cost)
    else:
        cost_str = cost_to_string(posting.cost)

    return f"{units_str} {{{cost_str}}}"


def _format_posting(posting: Posting, indent: int = 2) -> str:
    """Format a single posting line."""
    prefix = " " * indent
    parts = [prefix, posting.account]
    amount_str = _posting_to_string(posting)
    if amount_str:
        parts.append("  ")  # Two spaces before amount
        parts.append(amount_str)
    # Add price if present
    if posting.price is not None:
        parts.append(f" @ {amount_to_string(posting.price)}")
    if posting.flag:
        # Insert flag after indent, before account
        parts[1] = f"{posting.flag} {posting.account}"
    return "".join(parts)


def _format_meta(meta: dict, indent: int = 2) -> list[str]:
    """Format metadata lines (excluding internal keys)."""
    lines = []
    prefix = " " * indent
    for key, value in meta.items():
        if key.startswith("_") or key in ("filename", "lineno", "hash"):
            continue
        if isinstance(value, str):
            lines.append(f'{prefix}{key}: "{value}"')
        else:
            lines.append(f"{prefix}{key}: {value}")
    return lines


@to_string.register(Transaction)
def _format_transaction(
    entry: Transaction,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a transaction entry."""
    # Header line: date flag "payee" "narration" ^links #tags
    parts = [entry.date.isoformat(), entry.flag or "*"]
    if entry.payee:
        parts.append(f'"{entry.payee}"')
    parts.append(f'"{entry.narration}"')
    for link in sorted(entry.links):
        parts.append(f"^{link}")
    for tag in sorted(entry.tags):
        parts.append(f"#{tag}")
    lines = [" ".join(parts)]

    # Metadata
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))

    # Postings
    for posting in entry.postings:
        lines.append(_format_posting(posting, indent))
        # Posting metadata
        if posting.meta:
            posting_meta = dict(posting.meta)
            lines.extend(_format_meta(posting_meta, indent + 2))

    result = "\n".join(lines)
    return align(result, currency_column)


@to_string.register(Balance)
def _format_balance(
    entry: Balance,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a balance entry."""
    amount_str = amount_to_string(entry.amount)
    line = f"{entry.date.isoformat()} balance {entry.account}  {amount_str}"
    lines = [line]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    result = "\n".join(lines)
    return align(result, currency_column)


@to_string.register(Open)
def _format_open(
    entry: Open,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format an open entry."""
    parts = [entry.date.isoformat(), "open", entry.account]
    if entry.currencies:
        parts.append(", ".join(entry.currencies))
    if entry.booking:
        parts.append(f'"{entry.booking}"')
    lines = [" ".join(parts)]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Close)
def _format_close(
    entry: Close,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a close entry."""
    lines = [f"{entry.date.isoformat()} close {entry.account}"]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Price)
def _format_price(
    entry: Price,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a price entry."""
    amount_str = amount_to_string(entry.amount)
    lines = [f"{entry.date.isoformat()} price {entry.currency}  {amount_str}"]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    result = "\n".join(lines)
    return align(result, currency_column)


@to_string.register(Event)
def _format_event(
    entry: Event,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format an event entry."""
    # Event has 'type' attribute for event type
    event_type = getattr(entry, "type", "")
    description = getattr(entry, "description", "")
    lines = [f'{entry.date.isoformat()} event "{event_type}" "{description}"']
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Note)
def _format_note(
    entry: Note,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a note entry."""
    lines = [f'{entry.date.isoformat()} note {entry.account} "{entry.comment}"']
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Document)
def _format_document(
    entry: Document,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a document entry."""
    lines = [
        f'{entry.date.isoformat()} document {entry.account} "{entry.filename}"'
    ]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Pad)
def _format_pad(
    entry: Pad,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a pad entry."""
    lines = [
        f"{entry.date.isoformat()} pad {entry.account} {entry.source_account}"
    ]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Commodity)
def _format_commodity(
    entry: Commodity,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a commodity entry."""
    lines = [f"{entry.date.isoformat()} commodity {entry.currency}"]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Query)
def _format_query(
    entry: Query,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a query entry."""
    lines = [
        f'{entry.date.isoformat()} query "{entry.name}" "{entry.query_string}"'
    ]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Custom)
def _format_custom(
    entry: Custom,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format a custom entry."""
    parts = [entry.date.isoformat(), "custom", f'"{entry.type}"']
    for val in entry.values:
        # val is a CustomValue wrapper with .value attribute
        v = val.value if hasattr(val, "value") else val
        if isinstance(v, str):
            parts.append(f'"{v}"')
        else:
            parts.append(str(v))
    lines = [" ".join(parts)]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)


@to_string.register(Directive)
def _format_entry(
    entry: Directive,
    currency_column: int = 61,
    indent: int = 2,
) -> str:
    """Format any directive entry (fallback)."""
    # This is the fallback for directives not explicitly registered.
    # Try to detect the type and format appropriately.
    entry_type = type(entry).__name__

    # Build a basic representation
    date_str = entry.date.isoformat()

    if hasattr(entry, "narration"):
        # Transaction-like
        return _format_transaction(entry, currency_column, indent)  # type: ignore[arg-type]
    if hasattr(entry, "amount") and hasattr(entry, "account"):
        # Balance-like
        return _format_balance(entry, currency_column, indent)  # type: ignore[arg-type]
    if hasattr(entry, "currencies"):
        # Open-like
        return _format_open(entry, currency_column, indent)  # type: ignore[arg-type]

    # Generic fallback
    lines = [f"{date_str} {entry_type.lower()}"]
    meta = dict(entry.meta) if entry.meta else {}
    lines.extend(_format_meta(meta, indent))
    return "\n".join(lines)
