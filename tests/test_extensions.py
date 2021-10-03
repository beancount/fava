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


def test_before_insert_entry():
    """Extensions provide a before_insert_entry hook method."""
    hook_ledger = FavaLedger(
        data_file("extension-report-example.beancount")
    )

    assert bool(getattr(hook_ledger.extensions, "before_insert_entry"))

    hook_ledger.extensions.before_insert_entry("entry")
