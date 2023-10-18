"""Test importer for Fava."""

from __future__ import annotations

import csv
import datetime
from decimal import Decimal
from pathlib import Path

from beancount.core import amount
from beancount.core import data
from beancount.ingest import importer
from dateutil.parser import parse

from fava.beans import create

# mypy: ignore-errors


class TestImporter(importer.ImporterProtocol):
    """Test importer for Fava."""

    account = "Assets:Checking"
    currency = "EUR"

    def identify(self, file):
        return Path(file.name).name == "import.csv"

    def file_name(self, file):
        return f"examplebank.{Path(file.name).name}"

    def file_account(self, _):
        return self.account

    def file_date(self, _file):
        return datetime.date.today()

    def extract(self, file):
        entries = []
        index = 0
        with Path(file.name).open(encoding="utf-8") as file_:
            csv_reader = csv.DictReader(file_, delimiter=";")
            for index, row in enumerate(csv_reader):
                meta = data.new_metadata(file.name, index)
                meta["__source__"] = ";".join(list(row.values()))
                date = parse(row["Buchungsdatum"]).date()
                desc = f"{row['Umsatztext']}"

                if not row["IBAN"]:
                    entries.append(data.Note(meta, date, self.account, desc))
                else:
                    units_d = round(
                        Decimal(row["Betrag"].replace(",", ".")),
                        2,
                    )
                    units = amount.Amount(units_d, self.currency)

                    posting1 = data.Posting("", -units, None, None, None, None)
                    posting2 = data.Posting(
                        self.account,
                        units,
                        None,
                        None,
                        None,
                        None,
                    )
                    txn = data.Transaction(
                        meta,
                        date,
                        self.FLAG,
                        "",
                        desc,
                        set(),
                        set(),
                        [posting1, posting2],
                    )
                    entries.append(txn)

        if index:
            meta = data.new_metadata(file.name, 0)
            meta["__source__"] = "Balance"
            entries.append(
                create.balance(
                    meta,
                    datetime.date.today(),
                    self.account,
                    create.amount("10 USD"),
                ),
            )
        return entries


CONFIG = [
    TestImporter(),
]
