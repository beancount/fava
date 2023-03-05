"""Internal API.

This is used to pre-process some data that is used in the templates, allowing
this part of the functionality to be tested and allowing some end-to-end tests
for the frontend data validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from flask import current_app
from flask import url_for
from flask_babel import gettext  # type: ignore

from fava.context import g
from fava.core.accounts import AccountDict
from fava.core.fava_options import FavaOptions
from fava.helpers import BeancountError
from fava.util.excel import HAVE_EXCEL


@dataclass
class LedgerData:
    """This is used as report-independent data in the frontend."""

    accounts: list[str]
    account_details: AccountDict
    base_url: str
    currencies: list[str]
    errors: list[BeancountError]
    fava_options: FavaOptions
    incognito: bool
    have_excel: bool
    links: list[str]
    options: dict[str, Any]
    payees: list[str]
    precisions: dict[str, int]
    tags: list[str]
    years: list[str]
    user_queries: list[Any]
    upcoming_events_count: int
    extension_reports: list[tuple[str, str]]
    sidebar_links: list[tuple[str, str]]
    other_ledgers: list[tuple[str, str]]


def get_ledger_data() -> LedgerData:
    """Get the report-independent ledger data."""
    options = dict(g.ledger.options)
    del options["input_hash"]

    ledger = g.ledger

    return LedgerData(
        ledger.attributes.accounts,
        ledger.accounts,
        url_for("index"),
        ledger.attributes.currencies,
        ledger.errors,
        ledger.fava_options,
        current_app.config.get("INCOGNITO", False),
        HAVE_EXCEL,
        ledger.attributes.links,
        options,
        ledger.attributes.payees,
        ledger.format_decimal.precisions,
        ledger.attributes.tags,
        ledger.attributes.years,
        ledger.query_shell.queries[: ledger.fava_options.sidebar_show_queries],
        len(ledger.misc.upcoming_events),
        ledger.extensions.reports,
        ledger.misc.sidebar_links,
        [
            (ledger.options["title"], url_for("index", bfile=file_slug))
            for (file_slug, ledger) in current_app.config["LEDGERS"].items()
            if file_slug != g.beancount_file_slug
        ],
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


def _chart_net_worth() -> ChartData:
    return ChartData(
        "balances",
        gettext("Net Worth"),
        g.ledger.charts.net_worth(g.filtered, g.interval, g.conversion),
    )


def _chart_account_balance(account_name: str) -> ChartData:
    return ChartData(
        "balances",
        gettext("Account Balance"),
        g.ledger.charts.linechart(g.filtered, account_name, g.conversion),
    )


class ChartApi:
    """Functions to generate chart data."""

    account_balance = _chart_account_balance
    hierarchy = _chart_hierarchy
    interval_totals = _chart_interval_totals
    net_worth = _chart_net_worth
