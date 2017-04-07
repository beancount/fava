"""Attributes for auto-completion."""

from beancount.core import getters, realization
from beancount.core.data import Transaction
from beancount.utils.misc_utils import filter_type

from fava.core.helpers import FavaModule
from fava.util.ranking import ExponentialDecayRanker


class AttributesModule(FavaModule):
    """Some attributes of the ledger (mostly for auto-completion)."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.accounts = None
        self.currencies = None
        self.payees = None
        self.tags = None
        self.years = None

    def load_file(self):
        all_entries = self.ledger.all_entries
        self.tags = getters.get_all_tags(all_entries)
        self.years = list(getters.get_active_years(all_entries))[::-1]

        account_ranker = ExponentialDecayRanker(
            self.list_accounts(active_only=True))
        currency_ranker = ExponentialDecayRanker(
            self.ledger.options['commodities'])
        payee_ranker = ExponentialDecayRanker()

        for txn in filter_type(all_entries, Transaction):
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

    def list_accounts(self, active_only=False):
        """List all sub-accounts of the root account."""
        accounts = [child_account.account
                    for child_account in
                    realization.iter_children(self.ledger.all_root_account)
                    if not active_only or child_account.txn_postings]

        return accounts if active_only else accounts[1:]

    def payee_accounts(self, payee):
        """Rank accounts for the given payee."""
        account_ranker = ExponentialDecayRanker(self.accounts)
        for txn in filter_type(self.ledger.all_entries, Transaction):
            if txn.payee == payee:
                for posting in txn.postings:
                    account_ranker.update(posting.account, txn.date)
        return account_ranker.sort()
