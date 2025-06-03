"""Fava extension to test extension functionality.

# This can be used mainly for testing of the extension functionality
and usage of e.g. extension Javascript code or custom elements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from typing import TYPE_CHECKING

from flask import jsonify

from fava.context import g
from fava.core.charts import DateAndBalance
from fava.core.conversion import cost_or_value
from fava.core.inventory import SimpleCounterInventory
from fava.core.query import DecimalColumn
from fava.core.query import QueryResultTable
from fava.core.query import StrColumn
from fava.ext import extension_endpoint
from fava.ext import FavaExtensionBase
from fava.helpers import FavaAPIError
from fava.internal_api import BalancesChart

if TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response

    from fava.core.tree import SerialisedTreeNode
    from fava.core.tree import Tree
    from fava.core.tree import TreeNode


@dataclass(frozen=True)
class Portfolio:
    """A portfolio.

    Consists of a title and the result table to render.
    """

    title: str
    table: QueryResultTable


def _portfolio_data(nodes: list[TreeNode]) -> QueryResultTable:
    """Turn a portfolio of tree nodes into querytable-style data.

    Args:
        nodes: Account tree nodes.

    Returns:
        A QueryResultTable for the portfolio.
    """
    currency = g.ledger.options["operating_currency"][0]
    account_balances: list[tuple[str, Decimal | None]] = []
    total = Decimal()
    for node in nodes:
        balance = cost_or_value(node.balance, g.conv, g.ledger.prices)
        if currency in balance:
            balance_dec = balance[currency]
            total += balance_dec
            account_balances.append((node.name, balance_dec))
        else:
            account_balances.append((node.name, None))

    return QueryResultTable(
        [
            StrColumn("account"),
            DecimalColumn("balance"),
            DecimalColumn("allocation"),
        ],
        [
            (
                account,
                balance,
                (round((balance / total) * 100, 2) if balance else None),
            )
            for account, balance in account_balances
        ],
    )


def account_name_pattern_portfolio(tree: Tree, pattern: str) -> Portfolio:
    """Return portfolio info based on matching account name.

    Args:
        tree: Ledger root tree node.
        pattern: Account name regex pattern.

    Returns:
        A `Portfolio` for the accounts matching the pattern.
    """
    regexer = re.compile(pattern)
    selected_nodes = [
        node for account, node in tree.items() if regexer.match(account)
    ]
    return Portfolio(
        f"Account names matching: '{pattern}'",
        _portfolio_data(selected_nodes),
    )


def account_metadata_pattern_portfolio(
    tree: Tree,
    metadata_key: str,
    pattern: str,
) -> Portfolio:
    """Return portfolio info based on matching account open metadata.

    Args:
        tree: Ledger root tree node.
        metadata_key: Metadata key to match for in account open.
        pattern: Metadata value's regex pattern to match for.

    Returns:
        A `Portfolio` for the accounts with matching open metadata.
    """
    regexer = re.compile(pattern)
    selected_nodes = [
        tree[entry.account]
        for entry in g.ledger.all_entries_by_type.Open
        if metadata_key in entry.meta
        and regexer.match(str(entry.meta[metadata_key]))
    ]
    return Portfolio(
        f"Accounts with '{metadata_key}' metadata matching: '{pattern}'",
        _portfolio_data(selected_nodes),
    )


def portfolio_accounts(
    config: Any,
    filter_str: str | None = None,
) -> list[Portfolio]:
    """Get an account tree based on matching regex patterns."""
    tree = g.filtered.root_tree

    if filter_str:  # pragma: no cover
        return [account_name_pattern_portfolio(tree, filter_str)]

    portfolios = []
    for key, value in config:
        if key == "account_name_pattern":
            portfolios.append(account_name_pattern_portfolio(tree, value))
        elif key == "account_open_metadata_pattern":
            metadata_key, metadata_pattern = value
            portfolios.append(
                account_metadata_pattern_portfolio(
                    tree, metadata_key, metadata_pattern
                )
            )
        else:  # pragma: no cover
            msg = "Portfolio List: Invalid option."
            raise FavaAPIError(msg)

    return portfolios


class FavaExtTest(FavaExtensionBase):
    """Fava extension to test extension functionality."""

    report_title = "Fava extension test"

    has_js_module = True

    def portfolio_accounts(
        self,
        filter_str: str | None = None,
    ) -> list[Portfolio]:
        """Get an account tree based on matching regex patterns."""
        return portfolio_accounts(self.config, filter_str)

    @extension_endpoint
    def example_tree(self) -> SerialisedTreeNode:
        """Return a tree to render as a tree-table."""
        assets = g.ledger.options["name_assets"]
        return g.filtered.root_tree.get(assets).serialise_with_context()

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
