# pylint: disable=missing-docstring


def test_report_page_globals(extension_report_ledger):
    result = extension_report_ledger.extensions.reports
    assert result == [("PortfolioList", "Portfolio List")]
