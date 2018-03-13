import datetime

from fava.core import FavaLedger

from .conftest import data_file

FILE_PATH = data_file('import.beancount')
EXAMPLE = data_file('import.csv')


def test_ingest_examplefile():
    ingest_ledger = FavaLedger(FILE_PATH)
    identify_dir = list(ingest_ledger.ingest.identify_directory('.'))
    assert len(identify_dir) == 1

    filename, importers = identify_dir[0]
    importer_name = importers[0].name()
    entries = ingest_ledger.ingest.extract(filename, importer_name)
    assert len(entries) == 4
    assert entries[0].date == datetime.date(2017, 2, 12)
    assert entries[0].comment == 'Hinweis: Zinssatz auf 0,15% geändert'
    assert entries[1].date == datetime.date(2017, 2, 13)
    assert entries[1].narration == \
        'Payment to Company XYZ REF: 31000161205-6944556-0000463'
    assert entries[1].postings[0].account == ''
    assert entries[1].postings[0].units.number == 50.00
    assert entries[1].postings[0].units.currency == 'EUR'
    assert entries[1].postings[1].account == 'Assets:Checking'
    assert entries[1].postings[1].units.number == -50.00
    assert entries[1].postings[1].units.currency == 'EUR'
