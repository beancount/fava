"""Tests for the extension system."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .conftest import GetFavaLedger


def test_report_page_globals(get_ledger: GetFavaLedger) -> None:
    """Extensions can register reports."""
    extension_report_ledger = get_ledger("extension-report")
    result = extension_report_ledger.extensions.reports
    assert result == [("PortfolioList", "Portfolio List")]

    extension_report_ledger.extensions.after_write_source("test", "test")
