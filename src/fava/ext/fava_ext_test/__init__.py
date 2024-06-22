"""Fava extension to test extension functionality.

# This can be used mainly for testing of the extension functionality
and usage of e.g. extension Javascript code or custom elements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import NamedTuple
from typing import TYPE_CHECKING

from flask import jsonify

from fava.context import g
from fava.core.charts import DateAndBalance
from fava.core.conversion import cost_or_value
from fava.core.inventory import SimpleCounterInventory
from fava.ext import extension_endpoint
from fava.ext import FavaExtensionBase
from fava.helpers import FavaAPIError
from fava.internal_api import BalancesChart

if TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response

    from fava.beans.funcs import ResultType
    from fava.core.tree import Tree
    from fava.core.tree import TreeNode


class Row(NamedTuple):
    """A row in the portfolio tables."""

    account: str
    balance: Decimal | None
    allocation: Decimal | None


@dataclass
class Portfolio:
    """A portfolio."""

    title: str
    rows: list[Row]
    types: tuple[ResultType, ...] = (
        ("account", str),
        ("balance", Decimal),
        ("allocation", Decimal),
    )


class FavaExtTest(FavaExtensionBase):  # pragma: no cover
    """Fava extension to test extension functionality."""

    report_title = "Fava extension test"

    has_js_module = True

    def portfolio_accounts(
        self,
        filter_str: str | None = None,
    ) -> list[Portfolio]:
        """Get an account tree based on matching regex patterns."""
        tree = g.filtered.root_tree
        portfolios = []

        if filter_str:
            portfolio = self._account_name_pattern(tree, filter_str)
            portfolios.append(portfolio)
        else:
            for option in self.config:
                opt_key = option[0]
                if opt_key == "account_name_pattern":
                    portfolio = self._account_name_pattern(tree, option[1])
                elif opt_key == "account_open_metadata_pattern":
                    portfolio = self._account_metadata_pattern(
                        tree,
                        option[1][0],
                        option[1][1],
                    )
                else:
                    msg = "Portfolio List: Invalid option."
                    raise FavaAPIError(msg)
                portfolios.append(portfolio)

        return portfolios

    @extension_endpoint
    def example_data(self) -> Response:
        """Return some data with a GET endpoint."""
        return jsonify(["some data"])

    def chart_data(self) -> list[BalancesChart]:
        """Return some chart data."""
        return [
            BalancesChart(
                "nonsense data",
                [
                    DateAndBalance(
                        date(2023, 1, 1),
                        SimpleCounterInventory(EUR=Decimal(10)),
                    ),
                    DateAndBalance(
                        date(2023, 2, 1),
                        SimpleCounterInventory(EUR=Decimal(15)),
                    ),
                    DateAndBalance(
                        date(2023, 3, 1),
                        SimpleCounterInventory(EUR=Decimal(20)),
                    ),
                ],
            )
        ]

    def _account_name_pattern(self, tree: Tree, pattern: str) -> Portfolio:
        """Return portfolio info based on matching account name.

        Args:
            tree: Ledger root tree node.
            pattern: Account name regex pattern.

        Return:
            Data structured for use with a querytable (types, rows).
        """
        regexer = re.compile(pattern)
        selected_nodes = [
            node for acct, node in tree.items() if regexer.match(acct)
        ]
        return Portfolio(
            f"Account names matching: '{pattern}'",
            self._portfolio_data(selected_nodes),
        )

    def _account_metadata_pattern(
        self,
        tree: Tree,
        metadata_key: str,
        pattern: str,
    ) -> Portfolio:
        """Return portfolio info based on matching account open metadata.

        Args:
            tree: Ledger root tree node.
            metadata_key: Metadata key to match for in account open.
            pattern: Metadata value's regex pattern to match for.

        Return:
            Data structured for use with a querytable - (types, rows).
        """
        regexer = re.compile(pattern)
        selected_nodes = [
            tree[entry.account]
            for entry in self.ledger.all_entries_by_type.Open
            if metadata_key in entry.meta
            and regexer.match(str(entry.meta[metadata_key]))
        ]
        return Portfolio(
            f"Accounts with '{metadata_key}' metadata matching: '{pattern}'",
            self._portfolio_data(selected_nodes),
        )

    def _portfolio_data(self, nodes: list[TreeNode]) -> list[Row]:
        """Turn a portfolio of tree nodes into querytable-style data.

        Args:
            nodes: Account tree nodes.

        Return:
            types: Tuples of column names and types as strings.
            rows: Dictionaries of row data by column names.
        """
        operating_currency = self.ledger.options["operating_currency"][0]

        acct_balances: list[tuple[str, Decimal | None]] = []
        total = Decimal()
        for node in nodes:
            balance = cost_or_value(
                node.balance,
                g.conv,
                g.ledger.prices,
            )
            if operating_currency in balance:
                balance_dec = balance[operating_currency]
                total += balance_dec
                acct_balances.append((node.name, balance_dec))
            else:
                acct_balances.append((node.name, None))

        return [
            Row(
                account,
                bal,
                (round((bal / total) * 100, 2) if bal else None),
            )
            for account, bal in acct_balances
        ]
