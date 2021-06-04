"""Portfolio list extension for Fava.

This is a simple example of Fava's extension reports system.
"""
# mypy: ignore-errors
import re

from beancount.core.number import Decimal
from beancount.core.number import ZERO

from fava.ext import FavaExtensionBase
from fava.helpers import FavaAPIException
from fava.template_filters import cost_or_value


class PortfolioList(FavaExtensionBase):  # pragma: no cover
    """Sample Extension Report that just prints out an Portfolio List."""

    report_title = "Portfolio List"

    def portfolio_accounts(self):
        """An account tree based on matching regex patterns."""
        tree = self.ledger.root_tree
        portfolios = []

        for option in self.config:  # pylint: disable=not-an-iterable
            opt_key = option[0]
            if opt_key == "account_name_pattern":
                portfolio = self._account_name_pattern(tree, option[1])
            elif opt_key == "account_open_metadata_pattern":
                portfolio = self._account_metadata_pattern(
                    tree, option[1][0], option[1][1]
                )
            else:
                raise FavaAPIException("Portfolio List: Invalid option.")
            portfolios.append(portfolio)

        return portfolios

    def _account_name_pattern(self, tree, pattern):
        """
        Returns portfolio info based on matching account name.

        Args:
            tree: Ledger root tree node.
            pattern: Account name regex pattern.
        Return:
            Data structured for use with a querytable (types, rows).
        """
        title = "Account names matching: '" + pattern + "'"
        selected_accounts = []
        regexer = re.compile(pattern)
        for acct in tree.keys():
            if (regexer.match(acct) is not None) and (
                acct not in selected_accounts
            ):
                selected_accounts.append(acct)

        selected_nodes = [tree[x] for x in selected_accounts]
        portfolio_data = self._portfolio_data(selected_nodes)
        return title, portfolio_data

    def _account_metadata_pattern(self, tree, metadata_key, pattern):
        """
        Returns portfolio info based on matching account open metadata.

        Args:
            tree: Ledger root tree node.
            metadata_key: Metadata key to match for in account open.
            pattern: Metadata value's regex pattern to match for.
        Return:
            Data structured for use with a querytable - (types, rows).
        """
        title = (
            "Accounts with '"
            + metadata_key
            + "' metadata matching: '"
            + pattern
            + "'"
        )
        selected_accounts = []
        regexer = re.compile(pattern)
        for entry in self.ledger.all_entries_by_type.Open:
            if (metadata_key in entry.meta) and (
                regexer.match(entry.meta[metadata_key]) is not None
            ):
                selected_accounts.append(entry.account)

        selected_nodes = [tree[x] for x in selected_accounts]
        portfolio_data = self._portfolio_data(selected_nodes)
        return title, portfolio_data

    def _portfolio_data(self, nodes):
        """
        Turn a portfolio of tree nodes into querytable-style data.

        Args:
            nodes: Account tree nodes.
        Return:
            types: Tuples of column names and types as strings.
            rows: Dictionaries of row data by column names.
        """
        operating_currency = self.ledger.options["operating_currency"][0]
        acct_type = ("account", str(str))
        bal_type = ("balance", str(Decimal))
        alloc_type = ("allocation", str(Decimal))
        types = [acct_type, bal_type, alloc_type]

        rows = []
        portfolio_total = ZERO
        for node in nodes:
            row = {}
            row["account"] = node.name
            balance = cost_or_value(node.balance)
            if operating_currency in balance:
                balance_dec = balance[operating_currency]
                portfolio_total += balance_dec
                row["balance"] = balance_dec
            rows.append(row)

        for row in rows:
            if "balance" in row:
                row["allocation"] = round(
                    (row["balance"] / portfolio_total) * 100, 2
                )

        return types, rows
