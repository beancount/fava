from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest
from beancount.ingest.importer import (  # type: ignore[import-untyped]
    ImporterProtocol,
)

from fava.beans.abc import Amount
from fava.beans.abc import Note
from fava.beans.abc import Transaction
from fava.core.ingest import file_import_info
from fava.core.ingest import FileImporters
from fava.core.ingest import FileImportInfo
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger

    from .conftest import GetFavaLedger


def test_ingest_file_import_info(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
) -> None:
    class Imp(ImporterProtocol):  # type: ignore[misc]
        def __init__(self, acc: str) -> None:
            self.acc = acc

        def name(self) -> str:
            return self.acc

        def identify(self, file: Any) -> bool:
            return self.acc in file.name

    class Invalid(ImporterProtocol):  # type: ignore[misc]
        def __init__(self, acc: str) -> None:
            self.acc = acc

        def name(self) -> str:
            return self.acc

        def identify(self, file: Any) -> bool:
            return self.acc in file.name

        def file_account(self, _file: Any) -> bool:
            raise ValueError("Some error reason...")

    ingest_ledger = get_ledger("import")
    importer = next(iter(ingest_ledger.ingest.importers.values()))
    assert importer

    info = file_import_info(str(test_data_dir / "import.csv"), importer)
    assert info.account == "Assets:Checking"

    info2 = file_import_info("/asdf/basename", Imp("rawfile"))
    assert isinstance(info2.account, str)
    assert info2 == FileImportInfo(
        "rawfile",
        "",
        datetime.date.today(),
        "basename",
    )

    with pytest.raises(FavaAPIError) as err:
        file_import_info("/asdf/basename", Invalid("rawfile"))
    assert "Some error reason..." in err.value.message


def test_ingest_no_config(small_example_ledger: FavaLedger) -> None:
    assert not small_example_ledger.ingest.import_data()
    with pytest.raises(FavaAPIError):
        small_example_ledger.ingest.extract("import.csv", "import_name")


def test_ingest_examplefile(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
) -> None:
    ingest_ledger = get_ledger("import")

    files = ingest_ledger.ingest.import_data()
    files_with_importers = [f for f in files if f.importers]
    assert len(files) > 10  # all files in the test datafolder
    assert files_with_importers == [
        FileImporters(
            name=str(test_data_dir / "import.csv"),
            basename="import.csv",
            importers=[
                FileImportInfo(
                    "<run_path>.TestImporter",
                    "Assets:Checking",
                    datetime.date.today(),
                    "examplebank.import.csv",
                ),
            ],
        ),
    ]

    entries = ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestImporter",
    )
    assert len(entries) == 4
    assert entries[0].date == datetime.date(2017, 2, 12)
    assert isinstance(entries[0], Note)
    assert entries[0].comment == "Hinweis: Zinssatz auf 0,15% geändert"
    assert isinstance(entries[1], Transaction)
    assert entries[1].date == datetime.date(2017, 2, 13)
    assert (
        entries[1].narration
        == "Payment to Company XYZ REF: 31000161205-6944556-0000463"
    )
    assert not entries[1].postings[0].account
    assert isinstance(entries[1].postings[0].units, Amount)
    assert entries[1].postings[0].units.number == 50.00
    assert entries[1].postings[0].units.currency == "EUR"
    assert entries[1].postings[1].account == "Assets:Checking"
    assert isinstance(entries[1].postings[1].units, Amount)
    assert entries[1].postings[1].units.number == -50.00
    assert entries[1].postings[1].units.currency == "EUR"
    assert "__duplicate__" not in entries[1].meta
    assert "__duplicate__" in entries[2].meta


def test_filepath_in_primary_imports_folder(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", ["/test"])

    def _join(start: str, *args: str) -> Path:
        return Path(start).joinpath(*args).resolve()

    assert filepath_in_primary_imports_folder(
        "filename",
        example_ledger,
    ) == _join("/test", "filename")
    assert filepath_in_primary_imports_folder(
        "file/name",
        example_ledger,
    ) == _join("/test", "file name")
    assert filepath_in_primary_imports_folder(
        "/../file/name",
        example_ledger,
    ) == _join("/test", " .. file name")

    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", [])
    with pytest.raises(FavaAPIError):
        filepath_in_primary_imports_folder("filename", example_ledger)
