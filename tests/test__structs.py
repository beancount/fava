from __future__ import annotations

import datetime as dt

import pytest

from fava._structs import Close


def test_structs_are_frozen() -> None:
    close = Close(
        meta={},
        date=dt.date(2000, 1, 1),
        account="Assets:Cash",
    )
    with pytest.raises(AttributeError):
        close.account = "Throws"  # type: ignore[misc] # ty: ignore[invalid-assignment]
