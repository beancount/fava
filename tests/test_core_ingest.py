from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.beans.abc import Amount
from fava.beans.abc import Note
from fava.beans.abc import Transaction
from fava.beans.ingest import BeanImporterProtocol
from fava.core.ingest import file_import_info
from fava.core.ingest import FileImporters
from fava.core.ingest import FileImportInfo
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.helpers import FavaAPIError
from fava.serialisation import serialise
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.ingest import FileMemo
    from fava.core import FavaLedger

    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


def test_ingest_file_import_info(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
) -> None:
    class Imp(BeanImporterProtocol):
        def __init__(self, acc: str) -> None:
            self.acc = acc

        def name(self) -> str:
            return self.acc

        def identify(self, file: FileMemo) -> bool:
            return self.acc in file.name

        def file_account(self, _file: FileMemo) -> str:
            return self.acc

    class Invalid(BeanImporterProtocol):
        def __init__(self, acc: str) -> None:
            self.acc = acc

        def name(self) -> str:
            return self.acc

        def identify(self, file: FileMemo) -> bool:
            return self.acc in file.name

        def file_account(self, _file: FileMemo) -> str:
            msg = "Some error reason..."
            raise ValueError(msg)

    ingest_ledger = get_ledger("import")
    importer = next(iter(ingest_ledger.ingest.importers.values()))
    assert importer

    info = file_import_info(str(test_data_dir / "import.csv"), importer)
    assert info.account == "Assets:Checking"

    abs_path = str(Path("/asdf/basename").resolve(strict=False))
    info2 = file_import_info(abs_path, Imp("rawfile"))
    assert isinstance(info2.account, str)
    assert info2 == FileImportInfo(
        "rawfile",
        "rawfile",
        local_today(),
        "basename",
    )

    with pytest.raises(FavaAPIError) as err:
        file_import_info(abs_path, Invalid("rawfile"))
    assert "Some error reason..." in err.value.message


def test_ingest_no_config(small_example_ledger: FavaLedger) -> None:
    assert small_example_ledger.ingest.import_data() == []
    with pytest.raises(FavaAPIError):
        small_example_ledger.ingest.extract("import.csv", "import_name")


def test_ingest_examplefile(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
    snapshot: SnapshotFunc,
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
                    local_today(),
                    "examplebank.import.csv",
                ),
            ],
        ),
    ]

    entries = ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestImporter",
    )
    snapshot([serialise(e) for e in entries], json=True)
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
