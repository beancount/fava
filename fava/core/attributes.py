import collections
import math

from beancount.core import getters, realization
from beancount.core.data import Transaction
from beancount.utils.misc_utils import filter_type

from fava.core.helpers import FavaModule


class ExponentialDecayRanker(object):
    """Rank a list by exponential decay.

    Maintains scores for the items in a list. We can think of this as the sum
    of all 'likes', where the value of a 'like' starts at 1 and decays
    exponentially. So the current score would be given by (where `t` is the
    current time and `l` is the time of the 'like')

        s = Σ exp(-RATE * (t - l))

    As only the relative order on the items is relevant, we can multiply all
    scores by exp(RATE * t) and so we need to compute the following
    score:

        s = Σ exp(RATE * l)

    To avoid huge numbers, we actually compute and store the logarithm of that
    sum. The rate is set so that a 'like' from a year ago will count half as
    much as one from today.

    Args:
        list_: If given, this list is ranked is by ``.sort()`` otherwise all
               items with at least one 'like' will be ranked.
    """

    _RATE = math.log(2) * 1/365

    def __init__(self, list_=None):
        self.list = list_
        # We don't need to start with float('-inf') here as only the relative
        # scores matter.
        self.scores = collections.defaultdict(float)

    def update(self, item, date):
        """Add 'like' for item.

        Args:
            item: An item in the list that is being ranked.
            date: The date on which the item has been liked.
        """
        score = self.scores[item]
        time_ = date.toordinal()
        higher = max(score, time_ * self._RATE)
        lower = min(score, time_ * self._RATE)
        self.scores[item] = higher + math.log1p(math.exp(lower-higher))

    def _key(self, item):
        return self.scores.get(item, float())

    def sort(self):
        """Return items sorted by rank."""
        if self.list is None:
            return sorted(self.scores.keys(), key=self._key, reverse=True)
        return sorted(self.list, key=self._key, reverse=True)


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
