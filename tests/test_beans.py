from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from fava.beans.abc import Price
from fava.beans.account import parent
from fava.beans.prices import FavaPriceMap

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


def test_account_parent() -> None:
    assert parent("Assets") is None
    assert parent("Assets:Cash") == "Assets"
    assert parent("Assets:Cash:AA") == "Assets:Cash"
    assert parent("Assets:asdfasdf") == "Assets"


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
