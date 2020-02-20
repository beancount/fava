"""Attributes for auto-completion."""

from typing import List

from beancount.core import getters
from beancount.core.data import Transaction

from fava.core.helpers import FavaModule
from fava.util.ranking import ExponentialDecayRanker


class AttributesModule(FavaModule):
    """Some attributes of the ledger (mostly for auto-completion)."""

    def __init__(self, ledger) -> None:
        super().__init__(ledger)
        self.accounts: List[str] = []
        self.currencies: List[str] = []
        self.payees: List[str] = []
        self.links: List[str] = []
        self.tags: List[str] = []
        self.years: List[str] = []

    def load_file(self) -> None:
        all_entries = self.ledger.all_entries
        self.links = getters.get_all_links(all_entries)
        self.tags = getters.get_all_tags(all_entries)
        self.years = list(getters.get_active_years(all_entries))[::-1]

        account_ranker = ExponentialDecayRanker(
            sorted(self.ledger.accounts.keys())
        )
        currency_ranker = ExponentialDecayRanker(
            self.ledger.options["commodities"]
        )
        payee_ranker = ExponentialDecayRanker()

        transactions = self.ledger.all_entries_by_type[Transaction]
        for txn in transactions:
            if txn.payee:
                payee_ranker.update(txn.payee, txn.date)
            for posting in txn.postings:
                account_ranker.update(posting.account, txn.date)
                currency_ranker.update(posting.units.currency, txn.date)
                if posting.cost:
                    currency_ranker.update(posting.cost.currency, txn.date)

        self.accounts = account_ranker.sort()
        self.currencies = currency_ranker.sort()
        self.payees = payee_ranker.sort()

    def payee_accounts(self, payee: str) -> List[str]:
        """Rank accounts for the given payee."""
        account_ranker = ExponentialDecayRanker(self.accounts)
        transactions = self.ledger.all_entries_by_type[Transaction]
        for txn in transactions:
            if txn.payee == payee:
                for posting in txn.postings:
                    account_ranker.update(posting.account, txn.date)
        return account_ranker.sort()

    def payee_transaction(self, payee):
        """The last transaction for the given payee."""
        transactions = self.ledger.all_entries_by_type[Transaction]
        for txn in reversed(transactions):
            if txn.payee == payee:
                return txn
        return None
