"""Helpers to create entries."""

from __future__ import annotations

from typing import cast
from typing import overload
from typing import TYPE_CHECKING

from beancount.core import data
from beancount.core.amount import A as BEANCOUNT_A
from beancount.core.amount import Amount as BeancountAmount
from beancount.core.position import Cost as BeancountCost
from beancount.core.position import Position as BeancountPosition

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from decimal import Decimal

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


@overload
def amount(amt: Amount) -> Amount: ...  # pragma: no cover


@overload
def amount(amt: str) -> Amount: ...  # pragma: no cover


@overload
def amount(amt: Decimal, currency: str) -> Amount: ...  # pragma: no cover


def amount(amt: Amount | Decimal | str, currency: str | None = None) -> Amount:
    """Amount from a string or tuple."""
    if isinstance(amt, str):
        return BEANCOUNT_A(amt)  # type: ignore[return-value]
    if hasattr(amt, "number") and hasattr(amt, "currency"):
        return amt  # ty:ignore[invalid-return-type]
    if not isinstance(currency, str):  # pragma: no cover
        raise TypeError
    return BeancountAmount(amt, currency)  # type: ignore[return-value]


_amount = amount


def cost(
    number: Decimal,
    currency: str,
    date: datetime.date,
    label: str | None = None,
) -> Cost:
    """Create a Cost."""
    return BeancountCost(number, currency, date, label)


def position(units: Amount, cost: Cost | None) -> Position:
    """Create a Position."""
    return cast(
        "Position",
        BeancountPosition(
            units,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
            cost,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        ),
    )


def posting(
    account: str,
    units: Amount | str,
    cost: Cost | None = None,
    price: Amount | str | None = None,
    flag: str | None = None,
    meta: Meta | None = None,
) -> Posting:
    """Create a Beancount Posting."""
    if price is not None:
        price = amount(price)
    return data.Posting(  # type: ignore[return-value]
        account,
        amount(units),  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        cost,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        price,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        flag,
        dict(meta) if meta is not None else None,
    )  # ty:ignore[invalid-return-type]


_EMPTY_SET: frozenset[str] = frozenset()


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
    """Create a Beancount Transaction."""
    return cast(
        "Transaction",
        data.Transaction(
            dict(meta),
            date,
            flag,
            payee,
            narration,
            tags if tags is not None else _EMPTY_SET,
            links if links is not None else _EMPTY_SET,
            postings if postings is not None else [],  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        ),
    )


def balance(
    meta: Meta,
    date: datetime.date,
    account: str,
    amount: Amount | str,
    tolerance: Decimal | None = None,
    diff_amount: Amount | None = None,
) -> Balance:
    """Create a Beancount Balance."""
    return cast(
        "Balance",
        data.Balance(
            dict(meta),
            date,
            account,
            _amount(amount),  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
            tolerance,
            diff_amount,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        ),
    )


def close(
    meta: Meta,
    date: datetime.date,
    account: str,
) -> Close:
    """Create a Beancount Open."""
    return cast(
        "Close",
        data.Close(
            dict(meta),
            date,
            account,
        ),
    )


def document(
    meta: Meta,
    date: datetime.date,
    account: str,
    filename: str,
    tags: frozenset[str] | None = None,
    links: frozenset[str] | None = None,
) -> Document:
    """Create a Beancount Document."""
    return cast(
        "Document",
        data.Document(
            dict(meta),
            date,
            account,
            filename,
            tags,
            links,
        ),
    )


def note(
    meta: Meta,
    date: datetime.date,
    account: str,
    comment: str,
    tags: frozenset[str] | None = None,
    links: frozenset[str] | None = None,
) -> Note:
    """Create a Beancount Note."""
    return cast(
        "Note",
        data.Note(
            dict(meta),
            date,
            account,
            comment,
            tags,
            links,
        ),
    )


def open(  # noqa: A001
    meta: Meta,
    date: datetime.date,
    account: str,
    currencies: list[str],
    booking: data.Booking | None = None,
) -> Open:
    """Create a Beancount Open."""
    return cast(
        "Open",
        data.Open(
            dict(meta),
            date,
            account,
            currencies,
            booking,
        ),
    )
