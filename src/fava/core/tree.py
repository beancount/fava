"""Account balance trees."""
import collections
import datetime
from typing import List

from beancount.core import account
from beancount.core import convert
from beancount.core.data import Open

from fava.core.conversion import cost_or_value
from fava.core.inventory import CounterInventory


class TreeNode:
    """A node in the account tree."""

    __slots__ = ("name", "children", "balance", "balance_children", "has_txns")

    def __init__(self, name) -> None:
        #: Account name.
        self.name: str = name
        #: A list of :class:`.TreeNode`, its children.
        self.children: List["TreeNode"] = []
        #: The cumulative account balance.
        self.balance_children = CounterInventory()
        #: The account balance.
        self.balance = CounterInventory()
        #: Whether the account has any transactions.
        self.has_txns = False

    def serialise(self, conversion, price_map, end: datetime.date):
        """Serialise the account.

        Args:
            end: A date to use for cost conversions.
        """
        children = [
            child.serialise(conversion, price_map, end)
            for child in self.children
        ]
        return {
            "account": self.name,
            "balance_children": cost_or_value(
                self.balance_children, conversion, price_map, end
            ),
            "balance": cost_or_value(self.balance, conversion, price_map, end),
            "children": children,
        }


class Tree(dict):
    """Account tree.

    Args:
        entries: A list of entries to compute balances from.
    """

    def __init__(self, entries=None):
        dict.__init__(self)
        self.get("", insert=True)
        if entries:
            account_balances = collections.defaultdict(CounterInventory)
            for entry in entries:
                if isinstance(entry, Open):
                    self.get(entry.account, insert=True)
                for posting in getattr(entry, "postings", []):
                    account_balances[posting.account].add_position(posting)

            for name, balance in sorted(account_balances.items()):
                self.insert(name, balance)

    def ancestors(self, name):
        """Ancestors of an account.

        Args:
            name: An account name.
        Yields:
            The ancestors of the given account from the bottom up.
        """
        while name:
            name = account.parent(name)
            yield self.get(name)

    def insert(self, name, balance):
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

    def get(self, name, insert=False):
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
                    parent = self.get(account.parent(name), insert=True)
                    parent.children.append(node)
                self[name] = node
            return node

    def net_profit(self, options, account_name):
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
            account_name, income.balance_children + expenses.balance_children
        )

        return net_profit.get(account_name)

    def cap(self, options, unrealized_account):
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
                .balance_children.reduce(convert.get_cost)
                .items()
            }
        )

        # Add conversions
        self.insert(
            equity + ":" + options["account_current_conversions"], conversions
        )

        # Insert unrealized gains.
        self.insert(
            equity + ":" + unrealized_account, -self.get("").balance_children
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
