"""Type adapters for rustledger JSON to Fava-compatible Python objects.

This module provides concrete implementations of Fava's ABC types that
can be constructed from rustledger's JSON output.
"""

from __future__ import annotations

import datetime
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from decimal import Decimal
from typing import Any
from typing import TYPE_CHECKING

from rustfava.beans import abc

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence


class AsDictMixin:
    """Mixin that provides _asdict() method for compatibility with beancount's named tuples."""

    def _asdict(self) -> dict[str, Any]:
        """Return a dict of the dataclass fields, like named tuple _asdict()."""
        return {f.name: getattr(self, f.name) for f in fields(self)}  # type: ignore[arg-type]


class FrozenDict(dict[str, Any]):
    """A hashable dict for use in frozen dataclasses.

    This allows our directive types to be hashable while still
    providing dict-like access to metadata.
    """

    def __hash__(self) -> int:  # type: ignore[override]
        """Return hash based on sorted items, handling nested unhashable types."""
        def make_hashable(v: Any) -> Any:
            if isinstance(v, dict):
                return tuple(sorted((k, make_hashable(val)) for k, val in v.items()))
            if isinstance(v, list):
                return tuple(make_hashable(item) for item in v)
            return v

        return hash(tuple(sorted((k, make_hashable(v)) for k, v in self.items())))

    def __setitem__(self, key: Any, value: Any) -> None:
        """Prevent modification."""
        msg = "FrozenDict is immutable"
        raise TypeError(msg)

    def __delitem__(self, key: Any) -> None:
        """Prevent modification."""
        msg = "FrozenDict is immutable"
        raise TypeError(msg)

    def __copy__(self) -> dict[str, Any]:
        """Return a regular mutable dict copy."""
        return dict(self)

    def __deepcopy__(self, memo: dict[int, Any]) -> dict[str, Any]:
        """Return a regular mutable dict deep copy."""
        import copy

        return {copy.deepcopy(k, memo): copy.deepcopy(v, memo) for k, v in self.items()}


# Register our types with Fava's ABCs
# This allows isinstance() checks to work with our types


@dataclass(frozen=True, slots=True)
class RLAmount:
    """Rustledger Amount type."""

    number: Decimal
    currency: str

    @classmethod
    def from_json(cls, data: dict[str, Any] | None) -> RLAmount | None:
        """Create from JSON dict."""
        if data is None:
            return None
        return cls(
            number=Decimal(data["number"]),
            currency=data["currency"],
        )


@dataclass(frozen=True, slots=True)
class RLCost:
    """Rustledger Cost type."""

    number: Decimal | None
    currency: str
    date: datetime.date | None
    label: str | None
    number_total: Decimal | None = None

    @classmethod
    def from_json(
        cls,
        data: dict[str, Any] | None,
        default_date: datetime.date | None = None,
        units_number: Decimal | None = None,
    ) -> RLCost | None:
        """Create from JSON dict.

        Args:
            data: JSON dict with cost data
            default_date: Date to use if cost has no date (e.g., transaction date).
                         This matches beancount's behavior of filling in missing
                         cost dates with the transaction date.
            units_number: Number of units (for computing per-unit cost from total)
        """
        if data is None or not data:
            return None
        # Must have at least a currency to be a valid cost
        currency = data.get("currency")
        if not currency:
            return None
        # Use explicit date if provided, otherwise fall back to default_date
        cost_date = (
            datetime.date.fromisoformat(data["date"])
            if data.get("date")
            else default_date
        )
        # Handle both per-unit (number) and total cost (number_total)
        number = Decimal(data["number"]) if data.get("number") else None
        number_total = (
            Decimal(data["number_total"]) if data.get("number_total") else None
        )
        # If we have total cost but not per-unit, compute per-unit
        if number is None and number_total is not None and units_number:
            number = number_total / abs(units_number)
        return cls(
            number=number,
            currency=currency,
            date=cost_date,
            label=data.get("label"),
            number_total=number_total,
        )


@dataclass(frozen=True, slots=True)
class RLPosition:
    """Rustledger Position type."""

    units: RLAmount
    cost: RLCost | None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLPosition:
        """Create from JSON dict."""
        units = RLAmount.from_json(data["units"])
        if units is None:
            msg = "RLPosition requires units"
            raise ValueError(msg)
        return cls(
            units=units,
            cost=RLCost.from_json(
                data.get("cost"),
                units_number=units.number,
            ),
        )


abc.Position.register(RLPosition)


@dataclass(frozen=True, slots=True)
class RLPosting:
    """Rustledger Posting type."""

    account: str
    units: RLAmount | None
    cost: RLCost | None
    price: RLAmount | None
    flag: str | None
    meta: FrozenDict | None

    @classmethod
    def from_json(
        cls,
        data: dict[str, Any],
        transaction_date: datetime.date | None = None,
    ) -> RLPosting:
        """Create from JSON dict.

        Args:
            data: JSON dict with posting data
            transaction_date: The date of the parent transaction. Used to fill in
                            missing cost dates (beancount behavior).
        """
        meta = data.get("meta")
        units = RLAmount.from_json(data.get("units"))
        return cls(
            account=data["account"],
            units=units,
            cost=RLCost.from_json(
                data.get("cost"),
                default_date=transaction_date,
                units_number=units.number if units else None,
            ),
            price=RLAmount.from_json(data.get("price")),
            flag=data.get("flag"),
            meta=FrozenDict(meta) if meta else None,
        )


abc.Posting.register(RLPosting)


def _parse_date(date_str: str) -> datetime.date:
    """Parse ISO date string."""
    return datetime.date.fromisoformat(date_str)


def _parse_meta(data: dict[str, Any]) -> FrozenDict:
    """Parse metadata dict, converting date strings."""
    meta = dict(data.get("meta", {}))
    # Ensure filename and lineno are present with correct types
    if "filename" not in meta:
        meta["filename"] = "<unknown>"
    if "lineno" not in meta:
        meta["lineno"] = 0
    else:
        # Ensure lineno is int (FFI may return it as string)
        meta["lineno"] = int(meta["lineno"])
    return FrozenDict(meta)


@dataclass(frozen=True, slots=True)
class RLTransaction(AsDictMixin):
    """Rustledger Transaction type."""

    meta: Mapping[str, Any]
    date: datetime.date
    flag: str
    payee: str | None
    narration: str
    tags: frozenset[str]
    links: frozenset[str]
    postings: Sequence[RLPosting]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLTransaction:
        """Create from JSON dict."""
        txn_date = _parse_date(data["date"])
        return cls(
            meta=_parse_meta(data),
            date=txn_date,
            flag=data.get("flag", "*"),
            payee=data.get("payee"),
            narration=data.get("narration", ""),
            tags=frozenset(data.get("tags", [])),
            links=frozenset(data.get("links", [])),
            postings=tuple(
                RLPosting.from_json(p, transaction_date=txn_date)
                for p in data.get("postings", [])
            ),
        )


abc.Transaction.register(RLTransaction)


@dataclass(frozen=True, slots=True)
class RLBalance(AsDictMixin):
    """Rustledger Balance type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str
    amount: RLAmount
    tolerance: Decimal | None
    diff_amount: RLAmount | None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLBalance:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
            amount=RLAmount.from_json(data["amount"]),  # type: ignore[arg-type]
            tolerance=(
                Decimal(data["tolerance"]) if data.get("tolerance") else None
            ),
            diff_amount=RLAmount.from_json(data.get("diff_amount")),
        )


abc.Balance.register(RLBalance)


@dataclass(frozen=True, slots=True)
class RLOpen(AsDictMixin):
    """Rustledger Open type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str
    currencies: Sequence[str]
    booking: str | None  # Could be enum: FIFO, LIFO, HIFO, AVERAGE, STRICT, NONE

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLOpen:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
            currencies=tuple(data.get("currencies", [])),
            booking=data.get("booking"),
        )


abc.Open.register(RLOpen)


@dataclass(frozen=True, slots=True)
class RLClose(AsDictMixin):
    """Rustledger Close type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLClose:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
        )


abc.Close.register(RLClose)


@dataclass(frozen=True, slots=True)
class RLPrice(AsDictMixin):
    """Rustledger Price type."""

    meta: Mapping[str, Any]
    date: datetime.date
    currency: str
    amount: RLAmount

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLPrice:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            currency=data["currency"],
            amount=RLAmount.from_json(data["amount"]),  # type: ignore[arg-type]
        )


abc.Price.register(RLPrice)


@dataclass(frozen=True, slots=True)
class RLEvent(AsDictMixin):
    """Rustledger Event type."""

    meta: Mapping[str, Any]
    date: datetime.date
    type: str  # event_type
    description: str

    # Fava's Event ABC expects 'account' property but events don't have accounts
    # This is a quirk in Fava's ABC definition
    @property
    def account(self) -> str:
        """Event type (mapped to account for ABC compatibility)."""
        return self.type

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLEvent:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            type=data.get("event_type", ""),
            description=data.get("description", data.get("value", "")),
        )


abc.Event.register(RLEvent)


@dataclass(frozen=True, slots=True)
class RLNote(AsDictMixin):
    """Rustledger Note type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str
    comment: str
    tags: frozenset[str]
    links: frozenset[str]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLNote:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
            comment=data.get("comment", ""),
            tags=frozenset(data.get("tags", [])),
            links=frozenset(data.get("links", [])),
        )


abc.Note.register(RLNote)


@dataclass(frozen=True, slots=True)
class RLDocument(AsDictMixin):
    """Rustledger Document type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str
    filename: str
    tags: frozenset[str]
    links: frozenset[str]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLDocument:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
            filename=data.get("filename", data.get("path", "")),
            tags=frozenset(data.get("tags", [])),
            links=frozenset(data.get("links", [])),
        )


abc.Document.register(RLDocument)


@dataclass(frozen=True, slots=True)
class RLPad(AsDictMixin):
    """Rustledger Pad type."""

    meta: Mapping[str, Any]
    date: datetime.date
    account: str
    source_account: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLPad:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            account=data["account"],
            source_account=data["source_account"],
        )


abc.Pad.register(RLPad)


@dataclass(frozen=True, slots=True)
class RLCommodity(AsDictMixin):
    """Rustledger Commodity type."""

    meta: Mapping[str, Any]
    date: datetime.date
    currency: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLCommodity:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            currency=data["currency"],
        )


abc.Commodity.register(RLCommodity)


@dataclass(frozen=True, slots=True)
class RLQuery(AsDictMixin):
    """Rustledger Query (stored query) type."""

    meta: Mapping[str, Any]
    date: datetime.date
    name: str
    query_string: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLQuery:
        """Create from JSON dict."""
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            name=data["name"],
            query_string=data["query_string"],
        )


abc.Query.register(RLQuery)


@dataclass(frozen=True, slots=True)
class RLCustomValue:
    """Wrapper for custom directive values to match beancount's interface."""

    value: Any
    dtype: type = str  # Default to str type (not account)

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    @classmethod
    def from_raw(cls, raw_value: Any) -> RLCustomValue:
        """Create from raw value, parsing different value types.

        Rustledger outputs custom directive values as typed objects:
        - {"type": "string", "value": "text"} -> string
        - {"type": "number", "value": "10"} -> Decimal('10')
        - {"type": "bool", "value": true} -> bool
        - {"type": "amount", "value": {"number": "20.00", "currency": "EUR"}} -> RLAmount
        - {"type": "account", "value": "Expenses:Books"} -> string (account)
        - {"type": "date", "value": "2024-01-01"} -> datetime.date

        For backwards compatibility, also handles raw strings.
        """
        # Handle new typed format from rustledger
        if isinstance(raw_value, dict) and "type" in raw_value:
            val_type = raw_value["type"]
            val = raw_value.get("value")

            if val_type == "string":
                return cls(val, dtype=str)
            if val_type == "number":
                return cls(Decimal(str(val)), dtype=Decimal)
            if val_type == "bool":
                return cls(val, dtype=bool)
            if val_type == "amount":
                # Amount is a nested object with number and currency
                if isinstance(val, dict):
                    return cls(RLAmount.from_json(val))
                # Or pre-parsed string "20.00 EUR"
                parts = str(val).split()
                if len(parts) == 2:
                    return cls(RLAmount(number=Decimal(parts[0]), currency=parts[1]))
                return cls(val)
            if val_type == "account":
                return cls(val, dtype=str)
            if val_type == "date":
                if val is None:
                    return cls(None, dtype=datetime.date)
                return cls(datetime.date.fromisoformat(str(val)), dtype=datetime.date)
            # Unknown type, return as-is
            return cls(val)

        # Backwards compatibility: handle raw values without type info
        if not isinstance(raw_value, str):
            # Already typed (e.g., int, Decimal)
            return cls(raw_value)

        # Try to parse as Amount (number + currency)
        # Format: "20.00 EUR" or "-100.50 USD"
        parts = raw_value.split()
        if len(parts) == 2:
            try:
                number = Decimal(parts[0])
                currency = parts[1]
                # Verify currency looks like a currency (uppercase letters)
                if currency.isalpha() and currency.isupper():
                    return cls(RLAmount(number=number, currency=currency))
            except Exception:  # noqa: BLE001
                pass

        # Keep strings as strings - don't try to convert to numbers
        # When rustledger has typed values, numbers will come through
        # the dict branch above. For backwards compat, treat all
        # untyped strings as strings.
        return cls(raw_value)


@dataclass(frozen=True, slots=True)
class RLCustom(AsDictMixin):
    """Rustledger Custom type."""

    meta: Mapping[str, Any]
    date: datetime.date
    type: str  # custom_type
    values: Sequence[RLCustomValue]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RLCustom:
        """Create from JSON dict."""
        # Wrap values to match beancount's interface where values[i].value exists
        raw_values = data.get("values", [])
        wrapped_values = tuple(RLCustomValue.from_raw(v) for v in raw_values)
        return cls(
            meta=_parse_meta(data),
            date=_parse_date(data["date"]),
            type=data.get("custom_type", ""),
            values=wrapped_values,
        )


abc.Custom.register(RLCustom)


# Type mapping from JSON "type" field to constructor
DIRECTIVE_TYPES: dict[str, type] = {
    "transaction": RLTransaction,
    "balance": RLBalance,
    "open": RLOpen,
    "close": RLClose,
    "price": RLPrice,
    "event": RLEvent,
    "note": RLNote,
    "document": RLDocument,
    "pad": RLPad,
    "commodity": RLCommodity,
    "query": RLQuery,
    "custom": RLCustom,
}


def directive_from_json(data: dict[str, Any]) -> abc.Directive:
    """Convert a JSON directive to a Fava-compatible directive object.

    Args:
        data: JSON dict with 'type' field indicating directive type

    Returns:
        A directive instance registered with Fava's ABCs

    Raises:
        ValueError: If the directive type is unknown
    """
    directive_type = data.get("type", "").lower()
    cls = DIRECTIVE_TYPES.get(directive_type)
    if cls is None:
        msg = f"Unknown directive type: {directive_type}"
        raise ValueError(msg)
    # All types in DIRECTIVE_TYPES have from_json class method
    from_json = getattr(cls, "from_json")
    result: abc.Directive = from_json(data)
    return result


def directives_from_json(data: list[dict[str, Any]]) -> list[abc.Directive]:
    """Convert a list of JSON directives to Fava-compatible objects."""
    return [directive_from_json(d) for d in data]


# Reverse mapping from class to type name
_TYPE_NAMES: dict[type, str] = {v: k for k, v in DIRECTIVE_TYPES.items()}


def _amount_to_json(amt: RLAmount | None) -> dict[str, Any] | None:
    """Convert RLAmount to JSON dict."""
    if amt is None:
        return None
    return {"number": str(amt.number), "currency": amt.currency}


def _cost_to_json(cost: RLCost | None) -> dict[str, Any] | None:
    """Convert RLCostSpec to JSON dict."""
    if cost is None:
        return None
    result: dict[str, Any] = {}
    if cost.number is not None:
        result["number"] = str(cost.number)
    if cost.currency is not None:
        result["currency"] = cost.currency
    if cost.date is not None:
        result["date"] = str(cost.date)
    if cost.label is not None:
        result["label"] = cost.label
    return result if result else None


def _posting_to_json(posting: RLPosting) -> dict[str, Any]:
    """Convert RLPosting to JSON dict."""
    result: dict[str, Any] = {"account": posting.account}
    if posting.units is not None:
        result["units"] = _amount_to_json(posting.units)
    if posting.cost is not None:
        result["cost"] = _cost_to_json(posting.cost)
    if posting.price is not None:
        result["price"] = _amount_to_json(posting.price)
    if posting.flag:
        result["flag"] = posting.flag
    if posting.meta:
        result["meta"] = dict(posting.meta)
    return result


def directive_to_json(directive: abc.Directive) -> dict[str, Any]:
    """Convert a directive to JSON dict for rustledger.

    Args:
        directive: A Fava directive object

    Returns:
        JSON dict with 'type' field indicating directive type
    """
    cls = type(directive)
    type_name = _TYPE_NAMES.get(cls)

    if type_name is None:
        # Handle beancount types by checking class name
        cls_name = cls.__name__
        type_name = cls_name.lower().removeprefix("rl")
        if type_name not in DIRECTIVE_TYPES:
            msg = f"Unknown directive type: {cls}"
            raise ValueError(msg)

    result: dict[str, Any] = {
        "type": type_name,
        "date": str(directive.date),
    }

    # Add meta if present
    if hasattr(directive, "meta") and directive.meta:
        result["meta"] = dict(directive.meta)

    # Type-specific fields - use getattr since directive type varies
    if type_name == "transaction":
        result["flag"] = getattr(directive, "flag", "*")
        result["payee"] = getattr(directive, "payee", None)
        result["narration"] = getattr(directive, "narration", "")
        result["tags"] = list(getattr(directive, "tags", []))
        result["links"] = list(getattr(directive, "links", []))
        result["postings"] = [_posting_to_json(p) for p in getattr(directive, "postings", [])]

    elif type_name == "balance":
        result["account"] = getattr(directive, "account", "")
        result["amount"] = _amount_to_json(getattr(directive, "amount", None))
        tolerance = getattr(directive, "tolerance", None)
        if tolerance is not None:
            result["tolerance"] = str(tolerance)
        diff_amount = getattr(directive, "diff_amount", None)
        if diff_amount is not None:
            result["diff_amount"] = _amount_to_json(diff_amount)

    elif type_name == "open":
        result["account"] = getattr(directive, "account", "")
        currencies = getattr(directive, "currencies", None)
        result["currencies"] = list(currencies) if currencies else []
        result["booking"] = getattr(directive, "booking", None)

    elif type_name == "close":
        result["account"] = getattr(directive, "account", "")

    elif type_name == "price":
        result["currency"] = getattr(directive, "currency", "")
        result["amount"] = _amount_to_json(getattr(directive, "amount", None))

    elif type_name == "event":
        result["event_type"] = getattr(directive, "type", "")
        result["description"] = getattr(directive, "description", "")

    elif type_name == "note":
        result["account"] = getattr(directive, "account", "")
        result["comment"] = getattr(directive, "comment", "")
        result["tags"] = list(getattr(directive, "tags", []))
        result["links"] = list(getattr(directive, "links", []))

    elif type_name == "document":
        result["account"] = getattr(directive, "account", "")
        result["filename"] = getattr(directive, "filename", "")
        result["tags"] = list(getattr(directive, "tags", []))
        result["links"] = list(getattr(directive, "links", []))

    elif type_name == "pad":
        result["account"] = getattr(directive, "account", "")
        result["source_account"] = getattr(directive, "source_account", "")

    elif type_name == "commodity":
        result["currency"] = getattr(directive, "currency", "")

    elif type_name == "query":
        result["name"] = getattr(directive, "name", "")
        result["query_string"] = getattr(directive, "query_string", "")

    elif type_name == "custom":
        result["custom_type"] = getattr(directive, "type", "")
        # Custom values need special handling
        values = []
        for v in getattr(directive, "values", []):
            if isinstance(v, RLCustomValue):
                # Convert RLCustomValue to rustledger's typed format
                if v.dtype == str:
                    values.append({"type": "string", "value": str(v.value)})
                elif hasattr(v.value, "number") and hasattr(v.value, "currency"):
                    # Amount type
                    values.append({
                        "type": "amount",
                        "number": str(v.value.number),
                        "currency": v.value.currency,
                    })
                else:
                    values.append({"type": "string", "value": str(v.value)})
            elif hasattr(v, "_asdict"):
                values.append(v._asdict())
            else:
                values.append(v)
        result["values"] = values

    return result


def directives_to_json(directives: list[abc.Directive]) -> list[dict[str, Any]]:
    """Convert a list of directives to JSON dicts for rustledger."""
    return [directive_to_json(d) for d in directives]
