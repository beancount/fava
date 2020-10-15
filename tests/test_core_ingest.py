# pylint: disable=missing-docstring
import datetime

from .conftest import data_file
from fava.core import FavaLedger
from fava.core.ingest import file_import_info

FILE_PATH = data_file("import.beancount")
EXAMPLE = data_file("import.csv")


def test_ingest_file_import_info():
    ingest_ledger = FavaLedger(FILE_PATH)
    importer = next(iter(ingest_ledger.ingest.importers.values()))
    assert importer

    info = file_import_info(EXAMPLE, importer)
    assert info.account == "Assets:Checking"


def test_ingest_examplefile():
    ingest_ledger = FavaLedger(FILE_PATH)

    entries = ingest_ledger.ingest.extract(EXAMPLE, "<run_path>.TestImporter")
    assert len(entries) == 4
    assert entries[0].date == datetime.date(2017, 2, 12)
    assert entries[0].comment == "Hinweis: Zinssatz auf 0,15% geändert"
    assert entries[1].date == datetime.date(2017, 2, 13)
    assert (
        entries[1].narration
        == "Payment to Company XYZ REF: 31000161205-6944556-0000463"
    )
    assert entries[1].postings[0].account == ""
    assert entries[1].postings[0].units.number == 50.00
    assert entries[1].postings[0].units.currency == "EUR"
    assert entries[1].postings[1].account == "Assets:Checking"
    assert entries[1].postings[1].units.number == -50.00
    assert entries[1].postings[1].units.currency == "EUR"
    assert "__duplicate__" not in entries[1].meta
    assert "__duplicate__" in entries[2].meta
