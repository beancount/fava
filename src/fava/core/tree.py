"""Account balance trees."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from operator import attrgetter
from typing import Dict
from typing import Iterable
from typing import TYPE_CHECKING

from fava.beans.abc import Open
from fava.beans.account import parent as account_parent
from fava.context import g
from fava.core.conversion import AT_VALUE
from fava.core.conversion import cost_or_value
from fava.core.conversion import get_cost
from fava.core.inventory import CounterInventory

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Directive
    from fava.beans.prices import FavaPriceMap
    from fava.beans.types import BeancountOptions
    from fava.core.conversion import Conversion
    from fava.core.inventory import SimpleCounterInventory


@dataclass(frozen=True)
class SerialisedTreeNode:
    """A serialised TreeNode."""

    account: str
    balance: SimpleCounterInventory
    balance_children: SimpleCounterInventory
    children: list[SerialisedTreeNode]
    has_txns: bool


@dataclass(frozen=True)
class SerialisedTreeNodeWithCost(SerialisedTreeNode):
    """A serialised TreeNode with cost."""

    cost: SimpleCounterInventory
    cost_children: SimpleCounterInventory


class TreeNode:
    """A node in the account tree."""

    __slots__ = ("balance", "balance_children", "children", "has_txns", "name")

    def __init__(self, name: str) -> None:
        #: Account name.
        self.name: str = name
        #: A list of :class:`.TreeNode`, its children.
        self.children: list[TreeNode] = []
        #: The cumulative account balance.
        self.balance_children = CounterInventory()
        #: The account balance.
        self.balance = CounterInventory()
        #: Whether the account has any transactions.
        self.has_txns = False

    def serialise(
        self,
        conversion: str | Conversion,
        prices: FavaPriceMap,
        end: datetime.date | None,
        *,
        with_cost: bool = False,
    ) -> SerialisedTreeNode | SerialisedTreeNodeWithCost:
        """Serialise the account.

        Args:
            conversion: The conversion to use.
            prices: The price map to use.
            end: A date to use for cost conversions.
            with_cost: Additionally convert to cost.
        """
        children = [
            child.serialise(conversion, prices, end, with_cost=with_cost)
            for child in sorted(self.children, key=attrgetter("name"))
        ]
        return (
            SerialisedTreeNodeWithCost(
                self.name,
                cost_or_value(self.balance, conversion, prices, end),
                cost_or_value(self.balance_children, conversion, prices, end),
                children,
                self.has_txns,
                self.balance.reduce(get_cost),
                self.balance_children.reduce(get_cost),
            )
            if with_cost
            else SerialisedTreeNode(
                self.name,
                cost_or_value(self.balance, conversion, prices, end),
                cost_or_value(self.balance_children, conversion, prices, end),
                children,
                self.has_txns,
            )
        )

    def serialise_with_context(
        self,
    ) -> SerialisedTreeNode | SerialisedTreeNodeWithCost:
        """Serialise, getting all parameters from Flask context."""
        return self.serialise(
            g.conv,
            g.ledger.prices,
            g.filtered.end_date,
            with_cost=g.conv == AT_VALUE,
        )


class Tree(Dict[str, TreeNode]):
    """Account tree.

    Args:
        entries: A list of entries to compute balances from.
        create_accounts: A list of accounts that the tree should contain.
    """

    def __init__(
        self,
        entries: Iterable[Directive] | None = None,
        create_accounts: list[str] | None = None,
    ) -> None:
        super().__init__(self)
        self.get("", insert=True)
        if create_accounts:
            for account in create_accounts:
                self.get(account, insert=True)
        if entries:
            account_balances: dict[str, CounterInventory]
            account_balances = defaultdict(CounterInventory)
            for entry in entries:
                if isinstance(entry, Open):
                    self.get(entry.account, insert=True)
                for posting in getattr(entry, "postings", []):
                    account_balances[posting.account].add_position(posting)

            for name, balance in sorted(account_balances.items()):
                self.insert(name, balance)

    @property
    def accounts(self) -> list[str]:
        """The accounts in this tree."""
        return sorted(self.keys())

    def ancestors(self, name: str) -> Iterable[TreeNode]:
        """Ancestors of an account.

        Args:
            name: An account name.

        Yields:
            The ancestors of the given account from the bottom up.
        """
        while name:
            name = account_parent(name) or ""
            yield self.get(name)

    def insert(self, name: str, balance: CounterInventory) -> None:
        """Insert account with a balance.

        Insert account and update its balance and the balances of its
        ancestors.

        Args:
            name: An account name.
            balance: The balance of the account.
        """
        node = self.get(name, insert=True)
        node.balance.add_inventory(balance)
        node.balance_children.add_inventory(balance)
        node.has_txns = True
        for parent_node in self.ancestors(name):
            parent_node.balance_children.add_inventory(balance)

    def get(  # type: ignore[override]
        self,
        name: str,
        *,
        insert: bool = False,
    ) -> TreeNode:
        """Get an account.

        Args:
            name: An account name.
            insert: If True, insert the name into the tree if it does not
                exist.

        Returns:
            TreeNode: The account of that name or an empty account if the
            account is not in the tree.
        """
        try:
            return self[name]
        except KeyError:
            node = TreeNode(name)
            if insert:
                if name:
                    parent = self.get(account_parent(name) or "", insert=True)
                    parent.children.append(node)
                self[name] = node
            return node

    def net_profit(
        self,
        options: BeancountOptions,
        account_name: str,
    ) -> TreeNode:
        """Calculate the net profit.

        Args:
            options: The Beancount options.
            account_name: The name to use for the account containing the net
                profit.
        """
        income = self.get(options["name_income"])
        expenses = self.get(options["name_expenses"])

        net_profit = Tree()
        net_profit.insert(
            account_name,
            income.balance_children + expenses.balance_children,
        )

        return net_profit.get(account_name)

    def cap(self, options: BeancountOptions, unrealized_account: str) -> None:
        """Transfer Income and Expenses, add conversions and unrealized gains.

        Args:
            options: The Beancount options.
            unrealized_account: The name of the account to post unrealized
                gains to (as a subaccount of Equity).
        """
        equity = options["name_equity"]
        conversions = CounterInventory(
            {
                (currency, None): -number
                for currency, number in self.get("")
                .balance_children.reduce(get_cost)
                .items()
            },
        )

        # Add conversions
        self.insert(
            equity + ":" + options["account_current_conversions"],
            conversions,
        )

        # Insert unrealized gains.
        self.insert(
            equity + ":" + unrealized_account,
            -self.get("").balance_children,
        )

        # Transfer Income and Expenses
        self.insert(
            equity + ":" + options["account_current_earnings"],
            self.get(options["name_income"]).balance_children,
        )
        self.insert(
            equity + ":" + options["account_current_earnings"],
            self.get(options["name_expenses"]).balance_children,
        )
