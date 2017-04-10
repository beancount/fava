import csv
import datetime
import os
import pytest
from dateutil.parser import parse

from beancount.core.number import D
from beancount.core import data
from beancount.core import amount
from beancount.ingest import importer
from fava.core import FavaLedger


@pytest.fixture
def ingest_ledger(tmpdir):
    import_dirs = tmpdir.mkdir('downloads')
    import_config = tmpdir.mkdir('importers').join('import.config')
    import_config.write('CONFIG = []')

    bcontent = """
2017-01-01 custom "fava-option" "import-config" "{}"
2017-01-01 custom "fava-option" "import-dirs" "{}"
2017-01-01 open Assets:Checking
2017-01-01 open Expenses:Widgets
    """.format(import_config, import_dirs)
    bfile = tmpdir.join('example_import.beancount')
    bfile.write(bcontent)

    return FavaLedger(bfile)


class TestImporter(importer.ImporterProtocol):
    account = 'Assets:Checking'
    currency = 'EUR'

    def identify(self, file):
        return os.path.basename(file.name).startswith('example-bankfile')

    def file_name(self, file):
        return 'examplebank.{}'.format(os.path.basename(file.name))

    def file_account(self, _):
        return self.account

    def file_date(self, file):
        datetime.date()

    def extract(self, file):
        entries = []
        index = 0
        csv_reader = csv.DictReader(open(file.name), delimiter=';')
        for index, row in enumerate(csv_reader):
            meta = data.new_metadata(file.name, index)
            meta['__source__'] = ';'.join(list(row.values()))
            date = parse(row['Buchungsdatum']).date()
            desc = "{0[Umsatztext]}".format(row)
            units_d = round(D(row['Betrag'].replace(',', '.')), 2)
            units = amount.Amount(units_d, self.currency)

            posting1 = data.Posting('', -units, None, None, None, None)
            posting2 = data.Posting(self.account, units, None, None, None,
                                    None)
            txn = data.Transaction(meta, date, self.FLAG, '', desc,
                                   data.EMPTY_SET, data.EMPTY_SET,
                                   [posting1, posting2])

            entries.append(txn)

        if index:
            meta = data.new_metadata(file.name, 0)
            meta['__source__'] = 'Balance'
            entries.append(data.Balance(meta, datetime.date.today(),
                                        self.account, None, None, None))
        return entries


def test_ingest_examplefile(ingest_ledger):
    example_path = os.path.join(os.path.dirname(__file__), 'data')
    ingest_ledger.ingest.ingest_dirs = [example_path]
    ingest_ledger.ingest.config = [TestImporter()]

    importers = ingest_ledger.ingest.dirs_importers()
    assert len(importers) == 1
    assert importers[0][0] == example_path
    assert len(importers[0][1][0]['importers']) == 1
    assert importers[0][1][0]['importers'][0]['account'] == 'Assets:Checking'
    assert importers[0][1][0]['importers'][0]['name'] == \
        'tests.test_core_ingest.TestImporter'

    filename = importers[0][1][0]['filename']
    importer = importers[0][1][0]['importers'][0]['name']
    entries = ingest_ledger.ingest.extract(filename, importer)
    assert len(entries) == 3
    assert entries[0].date == datetime.date(2017, 2, 13)
    assert entries[0].narration == \
        'Payment to Company XYZ REF: 31000161205-6944556-0000463'
    assert entries[0].postings[0].account == ''
    assert entries[0].postings[0].units.number == 50.00
    assert entries[0].postings[0].units.currency == 'EUR'
    assert entries[0].postings[1].account == 'Assets:Checking'
    assert entries[0].postings[1].units.number == -50.00
    assert entries[0].postings[1].units.currency == 'EUR'
