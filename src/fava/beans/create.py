"""Helpers to create entries."""

from __future__ import annotations

from typing import overload
from typing import TYPE_CHECKING

from beancount.core import data
from beancount.core.amount import (  # type: ignore[attr-defined]
    A as BEANCOUNT_A,
)
from beancount.core.amount import Amount as BeancountAmount
from beancount.core.position import Position as BeancountPosition

from fava.beans.abc import Amount

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from decimal import Decimal

    from fava.beans.abc import Balance
    from fava.beans.abc import Cost
    from fava.beans.abc import Meta
    from fava.beans.abc import Position
    from fava.beans.abc import Posting
    from fava.beans.abc import TagsOrLinks
    from fava.beans.abc import Transaction
    from fava.beans.flags import Flag


@overload
def amount(amt: Amount) -> Amount: ...


@overload
def amount(amt: str) -> Amount: ...


@overload
def amount(amt: Decimal, currency: str) -> Amount: ...


def amount(amt: Amount | Decimal | str, currency: str | None = None) -> Amount:
    """Amount from a string or tuple."""
    if isinstance(amt, Amount):
        return amt
    if isinstance(amt, str):
        return BEANCOUNT_A(amt)  # type: ignore[no-any-return]
    if not isinstance(currency, str):
        raise TypeError
    return BeancountAmount(amt, currency)  # type: ignore[return-value]


def position(units: Amount, cost: Cost | None) -> Position:
    """Create a position."""
    return BeancountPosition(units, cost)  # type: ignore[arg-type,return-value]


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
        amount(units),  # type: ignore[arg-type]
        cost,  # type: ignore[arg-type]
        price,  # type: ignore[arg-type]
        flag,
        meta,
    )


def transaction(
    meta: Meta,
    date: datetime.date,
    flag: Flag,
    payee: str | None,
    narration: str,
    tags: TagsOrLinks,
    links: TagsOrLinks,
    postings: list[Posting],
) -> Transaction:
    """Create a Beancount Transaction."""
    return data.Transaction(  # type: ignore[return-value]
        meta,
        date,
        flag,
        payee,
        narration,
        tags,
        links,
        postings,  # type: ignore[arg-type]
    )


def balance(
    meta: Meta,
    date: datetime.date,
    account: str,
    _amount: Amount | str,
    tolerance: Decimal | None = None,
    diff_amount: Amount | None = None,
) -> Balance:
    """Create a Beancount Balance."""
    return data.Balance(  # type: ignore[return-value]
        meta,
        date,
        account,
        amount(_amount),  # type: ignore[arg-type]
        tolerance,
        diff_amount,  # type: ignore[arg-type]
    )


def note(
    meta: Meta,
    date: datetime.date,
    account: str,
    comment: str,
) -> Balance:
    """Create a Beancount Note."""
    return data.Note(  # type: ignore[return-value]
        meta,
        date,
        account,
        comment,
    )
