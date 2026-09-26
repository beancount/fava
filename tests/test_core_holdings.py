from __future__ import annotations

from datetime import date
from decimal import Decimal
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from fava.core import FavaLedger
from fava.core.holdings import HOLDINGS_QUERIES
from fava.core.holdings import holdings_query
from fava.core.query import QueryResultTable

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


@pytest.mark.parametrize("aggregation_key", list(HOLDINGS_QUERIES))
def test_holdings_query_pins_price_functions(aggregation_key: str) -> None:
    query = holdings_query(aggregation_key, date(2017, 8, 31))
    assert "value(sum(position), 2017-08-31)" in query
    assert "value(position, 2017-08-31)" in query
    if "getprice" in HOLDINGS_QUERIES[aggregation_key]:
        assert "getprice(currency, cost_currency, 2017-08-31)" in query


@pytest.mark.parametrize("aggregation_key", list(HOLDINGS_QUERIES))
def test_holdings_query_omits_date_without_filter(
    aggregation_key: str,
) -> None:
    query = holdings_query(aggregation_key, None)
    assert "value(sum(position), " not in query
    assert "value(position, " not in query
    assert "getprice(currency, cost_currency, " not in query
    assert "value(sum(position))" in query
    assert "value(position)" in query


def _account_market_value(
    table: QueryResultTable, account: str
) -> dict[str, Decimal]:
    names = [col.name for col in table.types]
    acc_i = names.index("account")
    val_i = names.index("market_value")
    row = next(r for r in table.rows if r[acc_i] == account)
    value = row[val_i]
    assert isinstance(value, dict)
    return value


def test_holdings_values_at_filter_end_date(tmp_path: Path) -> None:
    """Undated value() uses later prices; holdings must pin the filter end."""
    ledger_path = tmp_path / "prices.beancount"
    ledger_path.write_text(
        dedent("""\
            option "title" "Holdings Prices"
            option "operating_currency" "USD"

            2020-01-01 open Assets:Broker
            2020-01-01 open Assets:Cash USD
            2020-01-01 commodity STOCK

            2020-06-01 * "Buy"
              Assets:Broker  10 STOCK {10.00 USD}
              Assets:Cash   -100.00 USD

            2020-06-30 price STOCK 12.00 USD
            2020-09-30 price STOCK 20.00 USD
            """)
    )
    ledger = FavaLedger(str(ledger_path))
    filtered = ledger.get_filtered(time="2020-06")
    assert filtered.end_date == date(2020, 6, 30)

    undated = ledger.query_shell.execute_query_serialised(
        filtered.entries_with_all_prices,
        holdings_query("by_account", None),
    )
    dated = ledger.query_shell.execute_query_serialised(
        filtered.entries_with_all_prices,
        holdings_query("by_account", filtered.end_date),
    )
    assert isinstance(undated, QueryResultTable)
    assert isinstance(dated, QueryResultTable)
    assert _account_market_value(undated, "Assets:Broker") == {
        "USD": Decimal("200.00")
    }
    assert _account_market_value(dated, "Assets:Broker") == {
        "USD": Decimal("120.00")
    }
