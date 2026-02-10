from __future__ import annotations

from runpy import run_path
from typing import TYPE_CHECKING

import beangulp
import beangulp.extract

import fava
from fava.core import FavaLedger

if TYPE_CHECKING:
    from pathlib import Path


def test_example_import_cli(test_data_dir: Path) -> None:
    """Test that the importer is successful, when run directly on the data"""
    ledger = FavaLedger(str(test_data_dir / "import_for_docs.beancount"))
    mod = run_path(str(test_data_dir / "import_example_for_docs.py"))
    importer = mod["MyCSVImporter"]()
    file = test_data_dir / "import.csv"
    extract = beangulp.extract.extract_from_file(
        importer, file, ledger.all_entries
    )

    assert len(extract) == 3, (
        "Number lines read from import.csv is not correct. "
        "Should be 2 transactions and 1 balance"
    )
    assert [type(x).__name__ for x in extract] == [
        "Transaction",
        "Transaction",
        "Balance",
    ]


def test_example_import(test_data_dir: Path) -> None:
    ledger = FavaLedger(str(test_data_dir / "import_for_docs.beancount"))

    # This tests needs multiple steps as the User clicks multiple buttons until
    # the import starts

    ing = fava.core.IngestModule(ledger)
    # Read import configuration as defined in the fava option "import-config"
    ing.load_file()
    # Identify (file, importer) pairs based on the files it sees in the import
    # folder
    x = ing.import_data()

    # Only one file matches the importer we have defined
    x = [e for e in x if len(e.importers) != 0]
    assert len(x) == 1
    x0 = x[0]

    new_entries = ing.extract(x0.name, x0.importers[0].importer_name)

    assert len(new_entries) == 3, (
        "Number lines read from import.csv is not correct. "
        "Should be 2 transactions and 1 balance"
    )
    assert [type(x).__name__ for x in new_entries] == [
        "Transaction",
        "Transaction",
        "Balance",
    ]
