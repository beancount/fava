"""Tests for the extension system."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fava.core import FavaLedger

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_report_page_globals(test_data_dir: Path) -> None:
    """Extensions can register reports."""
    extension_report_ledger = FavaLedger(
        str(test_data_dir / "extension-report-example.beancount")
    )
    result = extension_report_ledger.extensions.reports
    assert result == [("PortfolioList", "Portfolio List")]

    extension_report_ledger.extensions.after_write_source("test", "test")
