"""Test importer for Fava."""

from __future__ import annotations

import csv
import datetime
from contextlib import suppress
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from beangulp import Importer

from fava.beans import create
from fava.beans.ingest import BeanImporterProtocol

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence
    from typing import Any

    from fava.beans.abc import Directive
    from fava.beans.ingest import FileMemo
    from fava.core.ingest import HookOutput

DATE = datetime.date(2022, 12, 12)


class TestBeangulpImporterNoExtraction(Importer):
    """Importer with the beangulp interface that doesn't extract entries."""

    def identify(self, filepath: str) -> bool:
        return Path(filepath).name == "import.csv"

    def account(self, filepath: str) -> str:  # noqa: ARG002
        return "Assets:Checking"

    def date(self, filepath: str) -> datetime.date:  # noqa: ARG002
        return DATE


class TestBeangulpImporter(TestBeangulpImporterNoExtraction):
    """Importer with the beangulp interface."""

    def extract(self, filepath: str, existing: Any) -> list[Directive]:  # noqa: ARG002
        entries: list[Directive] = []
        path = Path(filepath)
        account = self.account(filepath)
        currency = "EUR"

        with path.open(encoding="utf-8") as file_:
            csv_reader = csv.DictReader(file_, delimiter=";")
            for index, row in enumerate(csv_reader):
                meta: dict[str, str | int] = {
                    "filename": filepath,
                    "lineno": index,
                    "__source__": ";".join(list(row.values())),
                }
                date = datetime.date.fromisoformat(row["Buchungsdatum"])
                desc = row["Umsatztext"]

                if not row["IBAN"]:
                    entries.append(create.note(meta, date, account, desc))
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
                    frozenset(),
                    frozenset(),
                    [
                        create.posting(
                            "",
                            create.amount(-units_d, currency),
                        ),
                        create.posting(
                            account,
                            create.amount(units_d, currency),
                        ),
                    ],
                )
                entries.append(txn)

        if entries:
            bal = create.balance(
                {
                    "filename": filepath,
                    "lineno": 0,
                    "__source__": "Balance",
                },
                DATE,
                account,
                create.amount("10 USD"),
            )
            entries.append(bal)
        return entries


class TestImporter(BeanImporterProtocol):
    """Test importer for Fava."""

    account = "Assets:Checking"
    currency = "EUR"

    def identify(self, file: FileMemo) -> bool:
        return Path(file.name).name == "import.csv"

    def file_name(self, file: FileMemo) -> str:
        return f"examplebank.{Path(file.name).name}"

    def file_account(self, file: FileMemo) -> str:  # noqa: ARG002
        return self.account

    def file_date(self, file: FileMemo) -> datetime.date:  # noqa: ARG002
        return DATE

    def extract(
        self,
        file: FileMemo,
        **_kwargs: Any,
    ) -> list[Directive]:
        importer = TestBeangulpImporter()
        return importer.extract(file.name, existing=[])


class TestImporterThatErrorsOnExtract(TestImporter):
    def extract(
        self,
        file: FileMemo,  # noqa: ARG002
        **_kwargs: Any,
    ) -> list[Directive]:
        raise TypeError


def _example_noop_importer_hook(
    entries: HookOutput,
    existing: Sequence[Directive],  # noqa: ARG001
) -> HookOutput:
    return entries


HOOKS = [_example_noop_importer_hook]


with suppress(ImportError):  # pragma: no cover
    from beancount.ingest import extract  # type: ignore[import-untyped]

    HOOKS.append(extract.find_duplicate_entries)


CONFIG: list[BeanImporterProtocol | Importer] = [
    TestImporter(),
    TestImporterThatErrorsOnExtract(),
    TestBeangulpImporter(),
    TestBeangulpImporterNoExtraction(),
]
