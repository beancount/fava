"""Test importer for Fava."""

from __future__ import annotations

import csv
import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from fava.beans import create
from fava.beans.ingest import BeanImporterProtocol

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from fava.beans.abc import Directive
    from fava.beans.abc import Meta
    from fava.beans.ingest import FileMemo


class TestImporter(BeanImporterProtocol):
    """Test importer for Fava."""

    account = "Assets:Checking"
    currency = "EUR"

    def identify(self, file: FileMemo) -> bool:
        return Path(file.name).name == "import.csv"

    def file_name(self, file: FileMemo) -> str:
        return f"examplebank.{Path(file.name).name}"

    def file_account(self, _file: FileMemo) -> str:
        return self.account

    def file_date(self, _file: FileMemo) -> datetime.date:
        return datetime.date.today()  # noqa: DTZ011

    def extract(
        self,
        file: FileMemo,
        **_kwargs: Any,
    ) -> list[Directive]:
        entries: list[Directive] = []
        with Path(file.name).open(encoding="utf-8") as file_:
            csv_reader = csv.DictReader(file_, delimiter=";")
            for index, row in enumerate(csv_reader):
                meta: Meta = {
                    "filename": file.name,
                    "lineno": index,
                    "__source__": ";".join(list(row.values())),
                }
                date = datetime.date.fromisoformat(row["Buchungsdatum"])
                desc = row["Umsatztext"]

                if not row["IBAN"]:
                    entries.append(create.note(meta, date, self.account, desc))
                    continue

                units_d = round(
                    Decimal(row["Betrag"].replace(",", ".")),
                    2,
                )
                txn = create.transaction(
                    meta,
                    date,
                    "*",
                    "",
                    desc,
                    set(),
                    set(),
                    [
                        create.posting(
                            "",
                            create.amount(-units_d, self.currency),
                        ),
                        create.posting(
                            self.account,
                            create.amount(units_d, self.currency),
                        ),
                    ],
                )
                entries.append(txn)

        if entries:
            bal = create.balance(
                {
                    "filename": file.name,
                    "lineno": 0,
                    "__source__": "Balance",
                },
                self.file_date(file),
                self.account,
                create.amount("10 USD"),
            )
            entries.append(bal)
        return entries


CONFIG = [
    TestImporter(),
]
