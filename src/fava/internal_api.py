"""Internal API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import current_app
from flask import url_for

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
