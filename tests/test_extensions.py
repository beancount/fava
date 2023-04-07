"""Tests for the extension system."""
from __future__ import annotations

from pathlib import Path

from fava.core import FavaLedger


def test_report_page_globals(test_data_dir: Path) -> None:
    """Extensions can register reports."""
    extension_report_ledger = FavaLedger(
        str(test_data_dir / "extension-report-example.beancount")
    )
    result = extension_report_ledger.extensions.reports
    assert result == [("PortfolioList", "Portfolio List")]

    extension_report_ledger.extensions.after_write_source("test", "test")
