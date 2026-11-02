from __future__ import annotations

from pathlib import Path

import pytest

from fava.beans.abc import Transaction
from fava.core import FavaLedger

EXAMPLE_DIR = Path(__file__).parent.parent / "contrib" / "personal_ledger"


@pytest.fixture
def personal_ledger(monkeypatch: pytest.MonkeyPatch) -> FavaLedger:
    # In the example project, the package is installed into the venv.
    monkeypatch.syspath_prepend(EXAMPLE_DIR / "src")
    return FavaLedger(str(EXAMPLE_DIR / "ledger.beancount"))


def test_personal_ledger_import(personal_ledger: FavaLedger) -> None:
    assert not personal_ledger.errors

    csv_path = EXAMPLE_DIR / "downloads" / "bank-2026-03.csv"
    assert csv_path.exists()
    (file_importers,) = personal_ledger.ingest.import_data()
    assert file_importers.name == str(csv_path)
    (importer,) = file_importers.importers
    assert importer.account == "Assets:Checking"

    entries = personal_ledger.ingest.extract(
        str(csv_path), importer.importer_name
    )
    assert [
        (
            str(entry.date),
            entry.payee,
            [(p.account, str(p.units)) for p in entry.postings],
        )
        for entry in entries
        if isinstance(entry, Transaction)
    ] == [
        (
            "2026-03-02",
            "Supermarket",
            [
                ("Assets:Checking", "-52.10 EUR"),
                ("Expenses:Groceries", "None"),
            ],
        ),
        (
            "2026-03-31",
            "Employer",
            [
                ("Assets:Checking", "2500.00 EUR"),
                ("Income:Salary", "None"),
            ],
        ),
    ]
