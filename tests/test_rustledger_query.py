"""Tests for ``rustfava.rustledger.query._entries_to_source``.

Regression coverage for https://github.com/rustledger/rustfava/issues/144 —
the query-time serializer used to ignore the in-tree ``to_string``
formatter and silently drop tags, links, metadata, posting flags, cost
basis, prices, booking methods, and balance tolerance.
"""

from __future__ import annotations

import datetime
from decimal import Decimal

from rustfava.beans import create
from rustfava.rustledger.query import _convert_row_value
from rustfava.rustledger.query import _entries_to_source
from rustfava.rustledger.types import RLCustom
from rustfava.rustledger.types import RLCustomValue
from rustfava.rustledger.types import RLOpen


def test_entries_to_source_preserves_transaction_tags_links_and_metadata() -> None:
    postings = [
        create.posting(
            "Assets:US:Bank",
            "-1000.00 USD",
            flag="!",
            meta={"confidence": "high"},
        ),
        create.posting(
            "Assets:DE:Bank",
            "900.00 EUR",
            price="1.1111 USD",
        ),
    ]
    txn = create.transaction(
        {"category": "international"},
        datetime.date(2024, 2, 15),
        "*",
        "Wise",
        "USD->EUR transfer",
        tags=frozenset({"fx-2024"}),
        links=frozenset({"transfer-batch-12"}),
        postings=postings,
    )

    source = _entries_to_source([txn])

    # Tags + links must appear on the header.
    assert "#fx-2024" in source
    assert "^transfer-batch-12" in source
    # Directive metadata must survive.
    assert 'category: "international"' in source
    # Posting metadata must survive.
    assert 'confidence: "high"' in source
    # Per-posting flag must survive.
    assert "! Assets:US:Bank" in source
    # Per-posting price must survive (rustledger normalizes @@ to @).
    assert "@ 1.1111 USD" in source


def test_entries_to_source_preserves_cost_basis() -> None:
    postings = [
        create.posting(
            "Assets:US:Brokerage",
            "10 AAPL",
            cost=create.cost(Decimal("170.50"), "USD", datetime.date(2024, 3, 20)),
        ),
        create.posting("Assets:US:Bank", "-1705.00 USD"),
    ]
    txn = create.transaction(
        {},
        datetime.date(2024, 3, 20),
        "*",
        "Schwab",
        "Buy 10 AAPL",
        postings=postings,
    )

    source = _entries_to_source([txn])

    # `{price currency, date}` is what makes capital-gains math possible.
    assert "{170.50 USD, 2024-03-20}" in source


def test_entries_to_source_preserves_balance_tolerance() -> None:
    bal = create.balance(
        {},
        datetime.date(2024, 12, 31),
        "Assets:DE:Bank",
        "900.00 EUR",
        tolerance=Decimal("0.05"),
    )

    source = _entries_to_source([bal])

    assert "balance Assets:DE:Bank" in source
    assert "900.00 ~ 0.05 EUR" in source


def test_entries_to_source_preserves_open_booking_method() -> None:
    opn = RLOpen(
        meta={},
        date=datetime.date(2024, 1, 1),
        account="Assets:US:Brokerage",
        currencies=(),
        booking="STRICT",
    )

    source = _entries_to_source([opn])

    assert "open Assets:US:Brokerage" in source
    assert '"STRICT"' in source


def test_entries_to_source_skips_fava_custom_directives() -> None:
    # `custom "fava-option" ...` is not parseable by rledger and was
    # explicitly skipped in the old serializer; keep that behavior.
    fava_custom = RLCustom(
        meta={},
        date=datetime.date(2024, 1, 1),
        type="fava-option",
        values=(RLCustomValue("title", dtype=str), RLCustomValue("Test", dtype=str)),
    )
    other_custom = RLCustom(
        meta={},
        date=datetime.date(2024, 1, 1),
        type="budget",
        values=(RLCustomValue("Expenses:Food", dtype=str),),
    )

    source = _entries_to_source([fava_custom, other_custom])

    assert "fava-option" not in source
    assert "budget" in source


_INVENTORY_COL = {"name": "balance", "datatype": "Inventory"}


def test_inventory_sums_same_currency_cost_lots() -> None:
    """Regression for https://github.com/rustledger/rustfava/issues/155.

    Now that the serializer preserves cost basis, a balances query returns
    several positions of the same currency at different cost lots. Flattening
    the inventory to ``{currency: number}`` must accumulate; the old
    assignment kept only the last lot (e.g. 60 ITOT collapsed to 2).
    """
    value = {
        "positions": [
            {"units": {"number": "2", "currency": "ITOT"}},
            {"units": {"number": "3", "currency": "ITOT"}},
        ]
    }

    assert _convert_row_value(value, _INVENTORY_COL) == {"ITOT": Decimal("5")}


def test_inventory_mixed_currencies_and_lots() -> None:
    value = {
        "positions": [
            {"units": {"number": "2", "currency": "ITOT"}},
            {"units": {"number": "3", "currency": "ITOT"}},
            {"units": {"number": "100.00", "currency": "USD"}},
        ]
    }

    assert _convert_row_value(value, _INVENTORY_COL) == {
        "ITOT": Decimal("5"),
        "USD": Decimal("100.00"),
    }
