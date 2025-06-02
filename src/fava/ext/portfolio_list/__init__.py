"""Portfolio list extension for Fava.

This is a simple example of Fava's extension reports system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fava.ext import FavaExtensionBase
from fava.ext.fava_ext_test import portfolio_accounts

if TYPE_CHECKING:  # pragma: no cover
    from fava.ext.fava_ext_test import Portfolio


class PortfolioList(FavaExtensionBase):  # pragma: no cover
    """Sample Extension Report that just prints out an Portfolio List."""

    report_title = "Portfolio List"

    has_js_module = True

    def portfolio_accounts(
        self,
        filter_str: str | None = None,
    ) -> list[Portfolio]:
        """Get an account tree based on matching regex patterns."""
        return portfolio_accounts(self.config, filter_str)
