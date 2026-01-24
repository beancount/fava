"""Helpers to create entries."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import overload
from typing import TYPE_CHECKING

from fava.rustledger.types import FrozenDict
from fava.rustledger.types import RLAmount
from fava.rustledger.types import RLBalance
from fava.rustledger.types import RLClose
from fava.rustledger.types import RLCost
from fava.rustledger.types import RLDocument
from fava.rustledger.types import RLNote
from fava.rustledger.types import RLOpen
from fava.rustledger.types import RLPosting
from fava.rustledger.types import RLPosition
from fava.rustledger.types import RLTransaction

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Balance
    from fava.beans.abc import Close
    from fava.beans.abc import Document
    from fava.beans.abc import Meta
    from fava.beans.abc import Note
    from fava.beans.abc import Open
    from fava.beans.abc import Position
    from fava.beans.abc import Posting
    from fava.beans.abc import Transaction
    from fava.beans.flags import Flag
    from fava.beans.protocols import Amount
    from fava.beans.protocols import Cost


# Pattern to match amount strings like "100 USD", "-10.50 EUR", "1,000.00 CHF"
_AMOUNT_RE = re.compile(r"^\s*([-+]?\s*[\d,]+(?:\.\d*)?)\s+([A-Z][A-Z0-9'._-]*[A-Z0-9]?)\s*$")


def _parse_amount_string(amt_str: str) -> RLAmount:
    """Parse an amount string like '100 USD' into an RLAmount."""
    match = _AMOUNT_RE.match(amt_str)
    if not match:
        msg = f"Invalid amount string: {amt_str}"
        raise ValueError(msg)
    number_str, currency = match.groups()
    # Remove commas and spaces from number
    number_str = number_str.replace(",", "").replace(" ", "")
    return RLAmount(number=Decimal(number_str), currency=currency)


@overload
def amount(amt: Amount) -> Amount: ...  # pragma: no cover


@overload
def amount(amt: str) -> Amount: ...  # pragma: no cover


@overload
def amount(amt: Decimal, currency: str) -> Amount: ...  # pragma: no cover


def amount(amt: Amount | Decimal | str, currency: str | None = None) -> Amount:
    """Amount from a string or tuple."""
    if isinstance(amt, str):
        return _parse_amount_string(amt)  # type: ignore[return-value]
    if hasattr(amt, "number") and hasattr(amt, "currency"):
        return amt  # Already an Amount-like object
    if not isinstance(currency, str):  # pragma: no cover
        raise TypeError
    return RLAmount(amt, currency)  # type: ignore[return-value]


_amount = amount


def cost(
    number: Decimal,
    currency: str,
    date: datetime.date,
    label: str | None = None,
) -> Cost:
    """Create a Cost."""
    return RLCost(number, currency, date, label)  # type: ignore[return-value]


def position(units: Amount, cost: Cost | None) -> Position:
    """Create a Position."""
    # Convert units to RLAmount if needed
    if isinstance(units, str):
        units = _parse_amount_string(units)
    elif not isinstance(units, RLAmount):
        units = RLAmount(units.number, units.currency)

    # Convert cost to RLCost if needed
    rl_cost: RLCost | None = None
    if cost is not None:
        if isinstance(cost, RLCost):
            rl_cost = cost
        else:
            rl_cost = RLCost(
                number=cost.number,
                currency=cost.currency,
                date=cost.date,
                label=cost.label,
            )

    return RLPosition(units=units, cost=rl_cost)  # type: ignore[return-value]


def posting(
    account: str,
    units: Amount | str,
    cost: Cost | None = None,
    price: Amount | str | None = None,
    flag: str | None = None,
    meta: Meta | None = None,
) -> Posting:
    """Create a Posting."""
    # Convert units
    rl_units: RLAmount | None = None
    if units is not None:
        if isinstance(units, str):
            rl_units = _parse_amount_string(units)
        elif isinstance(units, RLAmount):
            rl_units = units
        else:
            rl_units = RLAmount(units.number, units.currency)

    # Convert cost
    rl_cost: RLCost | None = None
    if cost is not None:
        if isinstance(cost, RLCost):
            rl_cost = cost
        elif hasattr(cost, "number_per"):
            # CostSpec - convert to RLCost
            number = getattr(cost, "number_per", None)
            currency = getattr(cost, "currency", None)
            date = getattr(cost, "date", None)
            label = getattr(cost, "label", None)
            # Handle MISSING sentinels - MISSING is a class used as a value
            if number is not None and isinstance(number, type) and number.__name__ == "MISSING":
                number = None
            if currency is not None and isinstance(currency, type) and currency.__name__ == "MISSING":
                currency = None
            # Only create cost if we have a valid currency
            if currency is not None:
                rl_cost = RLCost(
                    number=number,
                    currency=currency,
                    date=date,
                    label=label,
                )
            # If both number and currency are MISSING, we still want to represent
            # an empty cost spec as "{}" in output - set cost to a sentinel
            elif number is None:
                # CostSpec with all MISSING - will be rendered as "{}"
                rl_cost = None  # Empty cost will be handled specially
        else:
            rl_cost = RLCost(
                number=cost.number,
                currency=cost.currency,
                date=cost.date,
                label=cost.label,
            )

    # Convert price
    rl_price: RLAmount | None = None
    if price is not None:
        if isinstance(price, str):
            rl_price = _parse_amount_string(price)
        elif isinstance(price, RLAmount):
            rl_price = price
        else:
            rl_price = RLAmount(price.number, price.currency)

    # Convert meta
    rl_meta: FrozenDict | None = None
    if meta is not None:
        rl_meta = FrozenDict(dict(meta))

    return RLPosting(  # type: ignore[return-value]
        account=account,
        units=rl_units,
        cost=rl_cost,
        price=rl_price,
        flag=flag,
        meta=rl_meta,
    )


_EMPTY_SET: frozenset[str] = frozenset()


def _make_meta(meta: Meta) -> FrozenDict:
    """Convert meta dict to FrozenDict."""
    return FrozenDict(dict(meta))


def transaction(
    meta: Meta,
    date: datetime.date,
    flag: Flag,
    payee: str | None,
    narration: str,
    tags: frozenset[str] | None = None,
    links: frozenset[str] | None = None,
    postings: list[Posting] | None = None,
) -> Transaction:
    """Create a Transaction."""
    # Convert postings to RLPosting if needed
    rl_postings: tuple[RLPosting, ...] = ()
    if postings:
        converted = []
        for p in postings:
            if isinstance(p, RLPosting):
                converted.append(p)
            else:
                # Convert from other posting type
                rl_units: RLAmount | None = None
                if p.units is not None:
                    if isinstance(p.units, RLAmount):
                        rl_units = p.units
                    else:
                        rl_units = RLAmount(p.units.number, p.units.currency)

                rl_cost: RLCost | None = None
                if p.cost is not None:
                    if isinstance(p.cost, RLCost):
                        rl_cost = p.cost
                    else:
                        rl_cost = RLCost(
                            number=p.cost.number,
                            currency=p.cost.currency,
                            date=p.cost.date,
                            label=p.cost.label,
                        )

                rl_price: RLAmount | None = None
                if p.price is not None:
                    if isinstance(p.price, RLAmount):
                        rl_price = p.price
                    else:
                        rl_price = RLAmount(p.price.number, p.price.currency)

                rl_meta: FrozenDict | None = None
                if p.meta:
                    rl_meta = FrozenDict(dict(p.meta))

                converted.append(RLPosting(
                    account=p.account,
                    units=rl_units,
                    cost=rl_cost,
                    price=rl_price,
                    flag=p.flag,
                    meta=rl_meta,
                ))
        rl_postings = tuple(converted)

    return RLTransaction(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        flag=flag or "*",
        payee=payee,
        narration=narration,
        tags=tags if tags is not None else _EMPTY_SET,
        links=links if links is not None else _EMPTY_SET,
        postings=rl_postings,
    )


def balance(
    meta: Meta,
    date: datetime.date,
    account: str,
    amount: Amount | str,
    tolerance: Decimal | None = None,
    diff_amount: Amount | None = None,
) -> Balance:
    """Create a Balance."""
    # Convert amount
    rl_amount: RLAmount
    if isinstance(amount, str):
        rl_amount = _parse_amount_string(amount)
    elif isinstance(amount, RLAmount):
        rl_amount = amount
    else:
        rl_amount = RLAmount(amount.number, amount.currency)

    # Convert diff_amount
    rl_diff: RLAmount | None = None
    if diff_amount is not None:
        if isinstance(diff_amount, RLAmount):
            rl_diff = diff_amount
        else:
            rl_diff = RLAmount(diff_amount.number, diff_amount.currency)

    return RLBalance(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        account=account,
        amount=rl_amount,
        tolerance=tolerance,
        diff_amount=rl_diff,
    )


def close(
    meta: Meta,
    date: datetime.date,
    account: str,
) -> Close:
    """Create a Close."""
    return RLClose(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        account=account,
    )


def document(
    meta: Meta,
    date: datetime.date,
    account: str,
    filename: str,
    tags: frozenset[str] | None = None,
    links: frozenset[str] | None = None,
) -> Document:
    """Create a Document."""
    return RLDocument(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        account=account,
        filename=filename,
        tags=tags if tags is not None else _EMPTY_SET,
        links=links if links is not None else _EMPTY_SET,
    )


def note(
    meta: Meta,
    date: datetime.date,
    account: str,
    comment: str,
    tags: frozenset[str] | None = None,
    links: frozenset[str] | None = None,
) -> Note:
    """Create a Note."""
    return RLNote(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        account=account,
        comment=comment,
        tags=tags if tags is not None else _EMPTY_SET,
        links=links if links is not None else _EMPTY_SET,
    )


def open(  # noqa: A001
    meta: Meta,
    date: datetime.date,
    account: str,
    currencies: list[str],
    booking: str | None = None,
) -> Open:
    """Create an Open."""
    return RLOpen(  # type: ignore[return-value]
        meta=_make_meta(meta),
        date=date,
        account=account,
        currencies=tuple(currencies),
        booking=booking,
    )
