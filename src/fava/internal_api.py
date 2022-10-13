"""Internal API.

This is used to pre-process some data that is used in the templates, allowing
this part of the functionality to be tested and allowing some end-to-end tests
for the frontend data validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from itertools import groupby
from operator import attrgetter
from typing import Any

from flask import current_app
from flask import url_for
from flask_babel import gettext  # type: ignore

from fava.context import g
from fava.core.accounts import AccountDict
from fava.core.fava_options import FavaOptions
from fava.util.excel import HAVE_EXCEL


@dataclass
class LedgerData:
    """This is used as report-independent data in the frontend."""

    accounts: list[str]
    account_details: AccountDict
    base_url: str
    currencies: list[str]
    errors: int
    fava_options: FavaOptions
    incognito: bool
    have_excel: bool
    links: list[str]
    options: dict[str, Any]
    payees: list[str]
    precisions: dict[str, int]
    tags: list[str]
    years: list[str]


def get_ledger_data() -> LedgerData:
    """Get the report-independent ledger data."""
    options = dict(g.ledger.options)
    del options["input_hash"]
    return LedgerData(
        g.ledger.attributes.accounts,
        g.ledger.accounts,
        url_for("index"),
        g.ledger.attributes.currencies,
        len(g.ledger.errors),
        g.ledger.fava_options,
        current_app.config.get("INCOGNITO", False),
        HAVE_EXCEL,
        g.ledger.attributes.links,
        options,
        g.ledger.attributes.payees,
        g.ledger.format_decimal.precisions,
        g.ledger.attributes.tags,
        g.ledger.attributes.years,
    )


@dataclass
class ChartData:
    """The common data format to pass charts to the frontend."""

    type: str
    label: str
    data: Any


def _chart_interval_totals(
    interval: str,
    account_name: str,
    label: str | None = None,
    invert: bool = False,
) -> ChartData:
    return ChartData(
        "bar",
        label or account_name,
        g.ledger.charts.interval_totals(
            g.filtered, interval, account_name, g.conversion, invert
        ),
    )


def _chart_hierarchy(
    account_name: str,
    begin_date: date | None = None,
    end_date: date | None = None,
    label: str | None = None,
) -> ChartData:
    return ChartData(
        "hierarchy",
        label or account_name,
        {
            "modifier": g.ledger.get_account_sign(account_name),
            "root": g.ledger.charts.hierarchy(
                g.filtered,
                account_name,
                g.conversion,
                begin_date,
                end_date or g.filtered.end_date,
            ),
        },
    )


def _chart_commodities() -> list[ChartData]:
    return [
        ChartData(
            "commodities",
            f"{base} / {quote}",
            {
                "prices": prices,
                "base": base,
                "quote": quote,
            },
        )
        for base, quote, prices in g.ledger.charts.prices(g.filtered)
    ]


def _chart_net_worth() -> ChartData:
    return ChartData(
        "balances",
        gettext("Net Worth"),
        g.ledger.charts.net_worth(g.filtered, g.interval, g.conversion),
    )


def _chart_events() -> list[ChartData]:
    events = g.filtered.events()
    charts = [ChartData("scatterplot", gettext("Events"), events)]
    key = attrgetter("type")
    for event_type, items in groupby(sorted(events, key=key), key):
        charts.append(
            ChartData(
                "scatterplot",
                gettext("Event: %(type)s", type=event_type),
                list(items),
            )
        )
    return charts


def _chart_account_balance(account_name: str) -> ChartData:
    return ChartData(
        "balances",
        gettext("Account Balance"),
        g.ledger.charts.linechart(g.filtered, account_name, g.conversion),
    )


class ChartApi:
    """Functions to generate chart data."""

    account_balance = _chart_account_balance
    commodities = _chart_commodities
    events = _chart_events
    hierarchy = _chart_hierarchy
    interval_totals = _chart_interval_totals
    net_worth = _chart_net_worth
