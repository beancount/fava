"""Attributes for auto-completion."""
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from beancount.core.data import Entries
from beancount.core.data import Transaction
from beancount.core.getters import get_active_years as getters_get_active_years
from beancount.core.getters import get_all_links
from beancount.core.getters import get_all_tags

from fava.core.module_base import FavaModule
from fava.util.date import FiscalYearEnd
from fava.util.ranking import ExponentialDecayRanker

if TYPE_CHECKING:
    from fava.core import FavaLedger


def get_active_years(entries: Entries, fye: FiscalYearEnd) -> List[str]:
    """Returns active years, with support for fiscal years.

    Args:
        entries: Beancount entries
        fye: fiscal year end

    Returns:
        A reverse sorted list of years or fiscal years that occur in the
        entries.
    """

    if fye == (12, 31):
        return sorted(
            map(str, getters_get_active_years(entries)), reverse=True
        )
    seen = set()
    month = fye.month
    day = fye.day
    for entry in entries:
        date = entry.date
        if date.month > month or date.month == month and date.day > day:
            seen.add(entry.date.year + 1)
        else:
            seen.add(entry.date.year)
    return [f"FY{year}" for year in sorted(seen, reverse=True)]


class AttributesModule(FavaModule):
    """Some attributes of the ledger (mostly for auto-completion)."""

    def __init__(self, ledger: "FavaLedger") -> None:
        super().__init__(ledger)
        self.accounts: List[str] = []
        self.currencies: List[str] = []
        self.payees: List[str] = []
        self.links: List[str] = []
        self.tags: List[str] = []
        self.years: List[str] = []

    def load_file(self) -> None:
        all_entries = self.ledger.all_entries
        self.links = get_all_links(all_entries)
        self.tags = get_all_tags(all_entries)
        self.years = get_active_years(
            all_entries, self.ledger.fava_options["fiscal-year-end"]
        )

        account_ranker = ExponentialDecayRanker(
            sorted(self.ledger.accounts.keys())
        )
        currency_ranker = ExponentialDecayRanker()
        payee_ranker = ExponentialDecayRanker()

        transactions = self.ledger.all_entries_by_type.Transaction
        for txn in transactions:
            if txn.payee:
                payee_ranker.update(txn.payee, txn.date)
            for posting in txn.postings:
                account_ranker.update(posting.account, txn.date)
                currency_ranker.update(
                    posting.units.currency, txn.date  # type: ignore
                )
                if posting.cost and posting.cost.currency is not None:
                    currency_ranker.update(posting.cost.currency, txn.date)

        self.accounts = account_ranker.sort()
        self.currencies = currency_ranker.sort()
        self.payees = payee_ranker.sort()

    def payee_accounts(self, payee: str) -> List[str]:
        """Rank accounts for the given payee."""
        account_ranker = ExponentialDecayRanker(self.accounts)
        transactions = self.ledger.all_entries_by_type.Transaction
        for txn in transactions:
            if txn.payee == payee:
                for posting in txn.postings:
                    account_ranker.update(posting.account, txn.date)
        return account_ranker.sort()

    def payee_transaction(self, payee: str) -> Optional[Transaction]:
        """The last transaction for the given payee."""
        transactions = self.ledger.all_entries_by_type.Transaction
        for txn in reversed(transactions):
            if txn.payee == payee:
                return txn
        return None
