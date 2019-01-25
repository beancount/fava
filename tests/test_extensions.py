# pylint: disable=missing-docstring


def test_report_page_globals(extension_report_ledger):
    result = extension_report_ledger.extensions.report_page_globals()
    assert result == [("PortfolioList", "Portfolio List", "")]
