"""Portfolio list extension for rustfava.

This is a simple example of rustfava's extension reports system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rustfava.ext import RustfavaExtensionBase
from rustfava.ext.rustfava_ext_test import portfolio_accounts

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.ext.rustfava_ext_test import Portfolio


class PortfolioList(RustfavaExtensionBase):  # pragma: no cover
    """Sample Extension Report that just prints out an Portfolio List."""

    report_title = "Portfolio List"

    has_js_module = True

    def portfolio_accounts(
        self,
        filter_str: str | None = None,
    ) -> list[Portfolio]:
        """Get an account tree based on matching regex patterns."""
        return portfolio_accounts(self.config, filter_str)
