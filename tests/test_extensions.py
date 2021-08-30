"""Tests for the extension system."""
from .conftest import data_file
from fava.core import FavaLedger


def test_report_page_globals():
    """Extensions can register reports."""
    extension_report_ledger = FavaLedger(
        data_file("extension-report-example.beancount")
    )
    result = extension_report_ledger.extensions.reports
    assert result == [("PortfolioList", "Portfolio List")]

    extension_report_ledger.extensions.after_write_source("test", "test")
