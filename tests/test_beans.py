from __future__ import annotations

import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.beans import create
from fava.beans.abc import Note
from fava.beans.abc import Price
from fava.beans.account import account_tester
from fava.beans.account import parent
from fava.beans.account import root
from fava.beans.funcs import get_position
from fava.beans.funcs import hash_entry
from fava.beans.helpers import replace
from fava.beans.prices import FavaPriceMap

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def test_account_parent() -> None:
    assert parent("Assets") is None
    assert parent("Assets:Cash") == "Assets"
    assert parent("Assets:Cash:AA") == "Assets:Cash"
    assert parent("Assets:asdfasdf") == "Assets"


def test_account_root() -> None:
    assert root("Assets:asdfasdf:asdfasdf") == "Assets"
    assert root("Assets:asdfasdf") == "Assets"


def test_account_tester() -> None:
    is_child = account_tester("Assets:Cash", with_children=True)
    assert not is_child("Assets")
    assert not is_child("Assets:CashOther")
    assert is_child("Assets:Cash")
    assert is_child("Assets:Cash:Test")

    is_equal = account_tester("Assets:Cash", with_children=False)
    assert not is_equal("Assets")
    assert not is_equal("Assets:CashOther")
    assert is_equal("Assets:Cash")
    assert not is_equal("Assets:Cash:Test")


def test_hash_entry() -> None:
    date = datetime.date(2022, 4, 2)
    note = create.note(
        {"filename": str(Path(__file__)), "lineno": 1},
        date,
        "Assets:Cash",
        "a note",
    )
    assert isinstance(hash_entry(note), str)
    str_hash = hash_entry("asdf")  # type: ignore[arg-type]
    assert isinstance(str_hash, str)


def test_get_position() -> None:
    date = datetime.date(2022, 4, 2)
    path = str(Path(__file__))
    note = create.note(
        {"filename": path, "lineno": 1}, date, "Assets:Cash", "a note"
    )

    assert get_position(note) == (path, 1)

    with pytest.raises(KeyError):
        get_position(replace(note, meta={}))

    with pytest.raises(ValueError, match="Invalid filename or lineno"):
        get_position(replace(note, meta={"filename": 1, "lineno": 1}))


def test_replace() -> None:
    date = datetime.date(2022, 4, 2)
    note = create.note(
        {"filename": str(Path(__file__)), "lineno": 1},
        date,
        "Assets:Cash",
        "a note",
    )
    assert note.comment == "a note"
    assert isinstance(note, Note)
    note_new = replace(note, comment="asdfasdf")
    assert note.comment == "a note"
    assert note_new.comment == "asdfasdf"

    with pytest.raises(TypeError):
        replace("", a="")  # type: ignore[type-var]


def test_fava_price_map(load_doc_entries: list[Directive]) -> None:
    """
    option "operating_currency" "CHF"
    option "operating_currency" "USD"

    1850-07-01 commodity CHF
    1792-04-02 commodity USD

    2020-12-18 price USD 0 ZEROUSD

    2020-12-18 price USD 0.88 CHF
    2022-12-19 price USD 0.9287 CHF
    2022-12-19 price USD 0.9288 CHF

    2021-11-12 open Assets:A CHF
    2019-05-01 open Assets:B CHF

    2022-12-19 *
        Assets:A  1 CHF
        Assets:B

    2022-12-27 *
        Assets:A  1 CHF
        Assets:B
    """

    price_entries = [e for e in load_doc_entries if isinstance(e, Price)]
    assert len(price_entries) == 4

    prices = FavaPriceMap(price_entries)
    assert prices.commodity_pairs([]) == [("USD", "CHF"), ("USD", "ZEROUSD")]
    assert prices.commodity_pairs(["USD", "CHF"]) == [
        ("CHF", "USD"),
        ("USD", "CHF"),
        ("USD", "ZEROUSD"),
    ]

    assert prices.get_all_prices(("NO", "PRICES")) is None
    assert prices.get_all_prices(("USD", "PRICES")) is None

    assert prices.get_price(("SAME", "SAME")) == Decimal(1)
    usd_chf = ("USD", "CHF")
    assert prices.get_all_prices(usd_chf) == [
        (datetime.date(2020, 12, 18), Decimal("0.88")),
        (datetime.date(2022, 12, 19), Decimal("0.9288")),
    ]

    assert prices.get_all_prices(("CHF", "USD")) == [
        (datetime.date(2020, 12, 18), Decimal(1) / Decimal("0.88")),
        (datetime.date(2022, 12, 19), Decimal(1) / Decimal("0.9288")),
    ]

    assert prices.get_price_point(usd_chf) == (
        datetime.date(2022, 12, 19),
        Decimal("0.9288"),
    )
    assert prices.get_price(usd_chf) == Decimal("0.9288")
    assert prices.get_price(usd_chf, datetime.date(2022, 12, 18)) == Decimal(
        "0.88",
    )
    assert prices.get_price(usd_chf, datetime.date(2022, 12, 19)) == Decimal(
        "0.9288",
    )
    assert prices.get_price(usd_chf, datetime.date(2022, 12, 20)) == Decimal(
        "0.9288",
    )
