"""Attributes for auto-completion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.util.date import END_OF_YEAR
from fava.util.ranking import ExponentialDecayRanker

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.beans.abc import Transaction
    from fava.core import FavaLedger
    from fava.util.date import FiscalYearEnd


def get_active_years(
    entries: list[Directive],
    fye: FiscalYearEnd,
) -> list[str]:
    """Return active years, with support for fiscal years.

    Args:
        entries: Beancount entries
        fye: fiscal year end

    Returns:
        A reverse sorted list of years or fiscal years that occur in the
        entries.
    """
    years = []
    if fye == END_OF_YEAR:
        prev_year = None
        for entry in entries:
            year = entry.date.year
            if year != prev_year:
                prev_year = year
                years.append(year)
        return [f"{year}" for year in reversed(years)]
    month = fye.month
    day = fye.day
    prev_year = None
    for entry in entries:
        date = entry.date
        year = (
            entry.date.year + 1
            if date.month > month or (date.month == month and date.day > day)
            else entry.date.year
        )
        if year != prev_year:
            prev_year = year
            years.append(year)
    return [f"FY{year}" for year in reversed(years)]


class AttributesModule(FavaModule):
    """Some attributes of the ledger (mostly for auto-completion)."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.accounts: list[str] = []
        self.currencies: list[str] = []
        self.payees: list[str] = []
        self.links: list[str] = []
        self.tags: list[str] = []
        self.years: list[str] = []

    def load_file(self) -> None:  # noqa: D102
        all_entries = self.ledger.all_entries

        all_links = set()
        all_tags = set()
        for entry in all_entries:
            links = getattr(entry, "links", None)
            if links is not None:
                all_links.update(links)
            tags = getattr(entry, "tags", None)
            if tags is not None:
                all_tags.update(tags)
        self.links = sorted(all_links)
        self.tags = sorted(all_tags)

        self.years = get_active_years(
            all_entries,
            self.ledger.fava_options.fiscal_year_end,
        )

        account_ranker = ExponentialDecayRanker(
            sorted(self.ledger.accounts.keys()),
        )
        currency_ranker = ExponentialDecayRanker()
        payee_ranker = ExponentialDecayRanker()

        for txn in self.ledger.all_entries_by_type.Transaction:
            if txn.payee:
                payee_ranker.update(txn.payee, txn.date)
            for posting in txn.postings:
                account_ranker.update(posting.account, txn.date)
                currency_ranker.update(posting.units.currency, txn.date)
                if posting.cost and posting.cost.currency is not None:
                    currency_ranker.update(posting.cost.currency, txn.date)

        self.accounts = account_ranker.sort()
        self.currencies = currency_ranker.sort()
        self.payees = payee_ranker.sort()

    def payee_accounts(self, payee: str) -> list[str]:
        """Rank accounts for the given payee."""
        account_ranker = ExponentialDecayRanker(self.accounts)
        transactions = self.ledger.all_entries_by_type.Transaction
        for txn in transactions:
            if txn.payee == payee:
                for posting in txn.postings:
                    account_ranker.update(posting.account, txn.date)
        return account_ranker.sort()

    def payee_transaction(self, payee: str) -> Transaction | None:
        """Get the last transaction for a payee."""
        transactions = self.ledger.all_entries_by_type.Transaction
        for txn in reversed(transactions):
            if txn.payee == payee:
                return txn
        return None
