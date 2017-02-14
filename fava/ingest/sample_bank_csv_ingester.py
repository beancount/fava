"""CSV-Importer for a sample bank.

This mainly serves as an example how to implement a Fava ingester.
"""
import csv
import difflib
from datetime import datetime

from beancount.core import amount, data
from beancount.core.number import D
from beancount.core.data import Transaction

from fava.ingest import IngestType, FavaIngestEntry, FavaIngestBase


def format_csv_line(row):
    label_line = list()
    value_line = list()
    for label, value in row.items():
        padding = max(len(str(label)), len(str(value)))
        label_line.append('{0:<{1}}'.format(label, padding))
        value_line.append('{0:<{1}}'.format(value, padding))
    return '// {}\n   {}'.format(' ; '.join(label_line),
                                 ' ; '.join(value_line))


class SampleBank(FavaIngestBase):
    def run_ingest(self, file, all_entries, payees, beancount_root):
        reader = csv.DictReader(file, delimiter=';')
        entries = []

        for lineno, row in enumerate(reader):
            date = datetime.strptime(row['Umsatzzeit'][:10], '%Y-%m-%d')
            number_str = row['Betrag'].replace('.', '').replace(',', '.')
            currency = row['Waehrung']
            # Bankomat, SEPA-Gutschrift, SEPA-Lastschrift, POS
            payee = row['Buchungstext']
            narration = row['Umsatztext'].strip()
            first_account = ''

            for word in narration.split(' '):
                if len(word) > 3:
                    result = difflib.get_close_matches(word, payees, 1)
                    if len(result):
                        payee = result[0]
                        matching_posting = self._matching_posting(payee,
                                                                  all_entries)
                        first_account = matching_posting.account

            entries.append(
                FavaIngestEntry(
                    line=lineno,
                    source=format_csv_line(row),
                    entry=data.Transaction(
                        None, date, '*', payee, narration, None, None, [
                            data.Posting(first_account,
                                         amount.Amount(D(number_str) * -1,
                                                       currency),
                                         None, None, None, None),
                            data.Posting('Assets:US:BofA:Checking', None, None,
                                         None, None, None)
                        ]),
                    type=IngestType.IMPORT
                )
            )

        return entries

    def _matching_posting(self, payee, entries):
        for entry in entries:
            if isinstance(entry, Transaction):
                if entry.payee == payee:
                    return entry.postings[0]
