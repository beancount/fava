"""Holdings report queries.

Beanquery's ``value()`` and ``getprice()`` use the latest price when no date
is given. Holdings queries run against ``entries_with_all_prices``, which
adds prices from outside the time filter back in, so an undated call would
value lots at future prices. Pin both functions to the filter end date
(the same date account reports use).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import datetime

_UNREALIZED_PROFIT_PCT = (
    "safediv((abs(sum(number(value(position{date}))))"
    " - abs(sum(number(cost(position))))),"
    " sum(number(cost(position)))) * 100 as unrealized_profit_pct"
)
_AVERAGE_COST = (
    "safediv(number(only(first(cost_currency), cost(sum(position)))),"
    " number(only(first(currency), units(sum(position))))) as average_cost"
)

HOLDINGS_QUERIES = {
    "all": f"""
SELECT
  account,
  units(sum(position)) as units,
  cost_number as cost,
  first(getprice(currency, cost_currency{{date}})) as price,
  cost(sum(position)) as book_value,
  value(sum(position){{date}}) as market_value,
  {_UNREALIZED_PROFIT_PCT},
  cost_date as acquisition_date
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY account, cost_date, currency, cost_currency, cost_number,
  account_sortkey(account)
ORDER BY account_sortkey(account), currency, cost_date
""".strip(),
    "by_account": f"""
SELECT
  account,
  units(sum(position)) as units,
  cost(sum(position)) as book_value,
  value(sum(position){{date}}) as market_value,
  {_UNREALIZED_PROFIT_PCT}
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY account, cost_currency, account_sortkey(account), currency
ORDER BY account_sortkey(account), currency
""".strip(),
    "by_currency": f"""
SELECT
  units(sum(position)) as units,
  {_AVERAGE_COST},
  first(getprice(currency, cost_currency{{date}})) as price,
  cost(sum(position)) as book_value,
  value(sum(position){{date}}) as market_value,
  {_UNREALIZED_PROFIT_PCT}
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY currency, cost_currency
ORDER BY currency, cost_currency
""".strip(),
    "by_cost_currency": f"""
SELECT
  units(sum(position)) as units,
  cost(sum(position)) as book_value,
  value(sum(position){{date}}) as market_value,
  {_UNREALIZED_PROFIT_PCT}
WHERE account_sortkey(account) ~ "^[01]"
GROUP BY cost_currency
ORDER BY cost_currency
""".strip(),
}


def holdings_query(
    aggregation_key: str, end_date: datetime.date | None
) -> str:
    """Return the holdings BQL, pinning prices to ``end_date`` when set.

    Args:
        aggregation_key: One of the keys in ``HOLDINGS_QUERIES``.
        end_date: Inclusive date to value at, or ``None`` for the latest price.

    Returns:
        The BQL string for the holdings report.
    """
    date_arg = f", {end_date.isoformat()}" if end_date is not None else ""
    return HOLDINGS_QUERIES[aggregation_key].format(date=date_arg)
