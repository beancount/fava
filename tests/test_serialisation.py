from __future__ import annotations

import datetime
import sys
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from beancount.core.number import MISSING
from beancount.core.position import CostSpec

from fava.beans import create
from fava.beans.helpers import replace
from fava.beans.str import to_string
from fava.core.charts import dumps
from fava.core.charts import loads
from fava.helpers import FavaAPIError
from fava.serialisation import deserialise
from fava.serialisation import deserialise_posting
from fava.serialisation import serialise

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from beancount.core.data import Meta

    from fava.beans.abc import Directive

    from .conftest import SnapshotFunc


def test_serialise_txn() -> None:
    txn = create.transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [
            create.posting("Assets:ETrade:Cash", "100 USD"),
            create.posting("Assets:ETrade:GLD", "0 USD"),
        ],
    )

    json_txn = {
        "date": "2017-12-12",
        "flag": "*",
        "meta": {},
        "narration": "asdfasd",
        "tags": ["tag"],
        "links": ["link"],
        "payee": "Test3",
        "t": "Transaction",
        "postings": [
            {"account": "Assets:ETrade:Cash", "amount": "100 USD"},
            {"account": "Assets:ETrade:GLD", "amount": "0 USD"},
        ],
    }

    serialised = loads(dumps(serialise(txn)))
    assert serialised == json_txn

    json_txn["payee"] = ""
    serialised = loads(dumps(serialise(replace(txn, payee=""))))
    assert serialised == json_txn

    serialised = loads(dumps(serialise(replace(txn, payee=None))))
    assert serialised == json_txn


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="skipped on Windows due to different absolute path",
)
def test_serialise_entry_types(
    snapshot: SnapshotFunc,
    load_doc_entries: list[Directive],
) -> None:
    """
    2017-12-11 open Assets:Cash USD "STRICT"
    2017-12-13 balance Assets:Cash 1 USD
    2017-12-14 balance Assets:Cash 1 ~ 1.0 USD
    2017-12-16 document Assets:Cash "/absolute/filename" #tag ^link
    2017-12-12 event "event name" "event description"
        bool-value: TRUE
        string-value: "value"
        account-value: Assets:Cash
        amount-value: 10 USD
        currency-value: USD
        number-value: 10 + 10
        date-value: 2022-12-12
    2017-12-20 note Assets:Cash "This is some comment or note"
    2017-12-21 pad Assets:Cash Assets:OtherCash
    2017-12-22 close Assets:Cash

    2018-12-15 commodity USD
    2018-12-16 price USD 1 EUR

    2019-12-12 query "query name" "journal"
    """
    snapshot([serialise(entry) for entry in load_doc_entries], json=True)


@pytest.mark.parametrize(
    ("amount_cost_price", "amount_string", "meta"),
    [
        (("100 USD", None, None), "100 USD", None),
        (("100 USD", None, None), "100 USD", {"someKey": "someValue"}),
        (
            (
                "100 USD",
                CostSpec(Decimal(10), None, "EUR", None, None, merge=False),
                None,
            ),
            "100 USD {10 EUR}",
            None,
        ),
        (
            (
                "100 USD",
                CostSpec(Decimal(10), None, "EUR", None, None, merge=False),
                "11 EUR",
            ),
            "100 USD {10 EUR} @ 11 EUR",
            None,
        ),
        (("100 USD", None, "11 EUR"), "100 USD @ 11 EUR", None),
        (
            (
                "100 USD",
                CostSpec(
                    MISSING,  # type: ignore[arg-type]
                    None,
                    MISSING,  # type: ignore[arg-type]
                    None,
                    None,
                    merge=False,
                ),
                None,
            ),
            "100 USD {}",
            None,
        ),
    ],
)
def test_serialise_posting(
    amount_cost_price: tuple[str, CostSpec | None, str],
    amount_string: str,
    meta: Meta | None,
) -> None:
    amount, cost, price = amount_cost_price
    pos = create.posting(
        "Assets",
        amount,
        cost,  # type: ignore[arg-type]
        price,
        flag=None,
        meta=meta,
    )
    json: dict[str, Any] = {"account": "Assets", "amount": amount_string}
    if meta:
        json["meta"] = meta
    assert loads(dumps(serialise(pos))) == json
    assert deserialise_posting(json) == pos


@pytest.mark.parametrize(
    ("amount_cost_price", "amount_string", "meta"),
    [
        (("100 USD", None, None), "10*10 USD", None),
        (("130 USD", None, None), "100+50 - 20 USD", {"someKey": "someValue"}),
        (("-140 USD", None, None), "-1400 / 10 USD", None),
        (("10 USD", None, "1 EUR"), "10 USD @@ 10 EUR", None),
        (
            ("7 USD", None, "1.428571428571428571428571429 EUR"),
            "7 USD @@ 10 EUR",
            None,
        ),
        (("0 USD", None, "0 EUR"), "0 USD @@ 0 EUR", None),
    ],
)
def test_deserialise_posting(
    amount_cost_price: tuple[str, CostSpec | None, str | None],
    amount_string: str,
    meta: Meta | None,
) -> None:
    """Roundtrip is not possible here due to total price or calculation."""
    amount, cost, price = amount_cost_price
    pos = create.posting(
        "Assets",
        amount,
        cost,  # type: ignore[arg-type]
        price,
        flag=None,
        meta=meta,
    )
    json: dict[str, Any] = {"account": "Assets", "amount": amount_string}
    if meta is not None:
        json["meta"] = meta
    assert deserialise_posting(json) == pos


def test_deserialise_posting_and_format(snapshot: SnapshotFunc) -> None:
    txn = create.transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [
            deserialise_posting({"account": "Assets", "amount": "10"}),
            deserialise_posting({"account": "Assets", "amount": "10 EUR @"}),
        ],
    )
    snapshot(to_string(txn))


def test_serialise_balance() -> None:
    bal = create.balance(
        {},
        datetime.date(2019, 9, 17),
        "Assets:ETrade:Cash",
        create.amount("0.1234567891011121314151617 CHF"),
        None,
        None,
    )

    json = {
        "date": "2019-09-17",
        "amount": {"currency": "CHF", "number": "0.1234567891011121314151617"},
        "diff_amount": None,
        "meta": {},
        "tolerance": None,
        "account": "Assets:ETrade:Cash",
        "t": "Balance",
    }

    serialised = loads(dumps(serialise(bal)))

    assert serialised == json


def test_deserialise() -> None:
    postings = [
        {"account": "Assets:ETrade:Cash", "amount": "100 USD"},
        {"account": "Assets:ETrade:GLD"},
    ]
    json_txn = {
        "t": "Transaction",
        "date": "2017-12-12",
        "flag": "*",
        "payee": "Test3",
        "narration": "asdfasd",
        "tags": ["tag"],
        "links": ["link"],
        "meta": {},
        "postings": postings,
    }

    txn = create.transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "Test3",
        "asdfasd",
        frozenset(["tag"]),
        frozenset(["link"]),
        [
            create.posting("Assets:ETrade:Cash", "100 USD"),
            replace(
                create.posting("Assets:ETrade:GLD", "100 USD"),
                units=MISSING,
            ),
        ],
    )
    assert deserialise(json_txn) == txn

    with pytest.raises(FavaAPIError):
        deserialise({})

    with pytest.raises(FavaAPIError):
        deserialise({"t": "NoEntry"})


def test_deserialise_balance() -> None:
    json_bal = {
        "t": "Balance",
        "date": "2017-12-12",
        "account": "Assets:ETrade:Cash",
        "amount": {"number": "100", "currency": "USD"},
        "meta": {},
    }
    bal = create.balance(
        {},
        datetime.date(2017, 12, 12),
        "Assets:ETrade:Cash",
        "100 USD",
    )
    assert deserialise(json_bal) == bal


def test_deserialise_note() -> None:
    json_note = {
        "t": "Note",
        "date": "2017-12-12",
        "account": "Assets:ETrade:Cash",
        "comment": 'This is some comment or note""',
        "meta": {},
    }
    note = create.note(
        {},
        datetime.date(2017, 12, 12),
        "Assets:ETrade:Cash",
        "This is some comment or note",
    )
    assert deserialise(json_note) == note
