"""Example importer and import hook for CSV files from a bank account."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from beancount.core import data
from beangulp.importers import csvbase

if TYPE_CHECKING:
    from beangulp.importer import Importer


class BankImporter(csvbase.Importer):
    """Import CSV files with the columns Date, Payee, Narration and Amount."""

    date = csvbase.Date("Date")
    payee = csvbase.Column("Payee")
    narration = csvbase.Column("Narration")
    amount = csvbase.Amount("Amount")

    def identify(self, filepath: str) -> bool:
        """Handle all CSV files whose name starts with "bank"."""
        path = Path(filepath)
        return path.name.startswith("bank") and path.suffix == ".csv"


#: Accounts to book the other side of imported transactions to, by payee.
CATEGORIES = {
    "Employer": "Income:Salary",
    "Supermarket": "Expenses:Groceries",
}


def categorize(
    extracted: list[tuple[str, list[data.Directive], str, Importer]],
    existing_entries: list[data.Directive],  # noqa: ARG001
) -> list[tuple[str, list[data.Directive], str, Importer]]:
    """Import hook to add a balancing posting for payees in CATEGORIES."""

    def add_category(entry: data.Directive) -> data.Directive:
        if not isinstance(entry, data.Transaction):
            return entry
        account = CATEGORIES.get(entry.payee or "")
        if account is None:
            return entry
        posting = data.Posting(account, None, None, None, None, None)
        return entry._replace(postings=[*entry.postings, posting])

    return [
        (filename, [add_category(entry) for entry in entries], account, imp)
        for filename, entries, account, imp in extracted
    ]
