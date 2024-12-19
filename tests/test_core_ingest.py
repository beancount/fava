from __future__ import annotations

import datetime
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.beans import BEANCOUNT_V3
from fava.beans.abc import Amount
from fava.beans.abc import Note
from fava.beans.abc import Transaction
from fava.beans.ingest import BeanImporterProtocol
from fava.core.ingest import file_import_info
from fava.core.ingest import FileImportInfo
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.core.ingest import get_name
from fava.core.ingest import ImportConfigLoadError
from fava.core.ingest import importer_identify
from fava.core.ingest import ImporterExtractError
from fava.core.ingest import load_import_config
from fava.helpers import FavaAPIError
from fava.serialisation import serialise
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.ingest import FileMemo
    from fava.core import FavaLedger

    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


def test_ingest_file_import_info(
    test_data_dir: Path, get_ledger: GetFavaLedger
) -> None:
    ingest_ledger = get_ledger("import")
    importer = next(iter(ingest_ledger.ingest.importers.values()))
    assert importer

    csv_path = test_data_dir / "import.csv"
    info = file_import_info(csv_path, importer)
    assert info.account == "Assets:Checking"


class MinimalImporter(BeanImporterProtocol):
    def __init__(self, acc: str = "Assets:Checking") -> None:
        self.acc = acc

    def name(self) -> str:
        return self.acc

    def identify(self, file: FileMemo) -> bool:
        return self.acc in file.name

    def file_account(self, _file: FileMemo) -> str:
        return self.acc


def test_ingest_file_import_info_minimal_importer(test_data_dir: Path) -> None:
    csv_path = test_data_dir / "import.csv"

    info = file_import_info(csv_path, MinimalImporter("rawfile"))
    assert isinstance(info.account, str)
    assert info == FileImportInfo(
        "rawfile",
        "rawfile",
        local_today(),
        "import.csv",
    )


class AccountNameErrors(MinimalImporter):
    def file_account(self, _file: FileMemo) -> str:
        msg = "Some error reason..."
        raise ValueError(msg)


def test_ingest_file_import_info_account_method_errors(
    test_data_dir: Path,
) -> None:
    csv_path = test_data_dir / "import.csv"

    with pytest.raises(FavaAPIError) as err:
        file_import_info(csv_path, AccountNameErrors())
    assert "Some error reason..." in err.value.message


class IdentifyErrors(MinimalImporter):
    def identify(self, _file: FileMemo) -> bool:
        msg = "IDENTIFY_ERRORS"
        raise ValueError(msg)


def test_ingest_identify_errors(test_data_dir: Path) -> None:
    csv_path = test_data_dir / "import.csv"

    with pytest.raises(FavaAPIError) as err:
        importer_identify(IdentifyErrors(), csv_path)
    assert "IDENTIFY_ERRORS" in err.value.message


class ImporterNameErrors(MinimalImporter):
    def name(self) -> str:
        msg = "GET_NAME_WILL_ERROR"
        raise ValueError(msg)


def test_ingest_get_name_errors() -> None:
    with pytest.raises(FavaAPIError) as err:
        get_name(ImporterNameErrors())
    assert "GET_NAME_WILL_ERROR" in err.value.message


@pytest.mark.skipif(
    sys.platform == "win32", reason="different error on windows"
)
def test_load_import_config() -> None:
    with pytest.raises(ImportConfigLoadError, match=r".*ImportError.*"):
        load_import_config(Path(__file__).parent)

    with pytest.raises(ImportConfigLoadError, match=r".*CONFIG is missing.*"):
        load_import_config(Path(__file__))


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
    assert len(files) > 10  # all files in the test datafolder

    with pytest.raises(ImporterExtractError):
        entries = ingest_ledger.ingest.extract(
            str(test_data_dir / "import.csv"),
            "<run_path>.TestImporterThatErrorsOnExtrac",
        )
    entries = ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestBeangulpImporterNoExtraction",
    )
    assert not entries

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
    if not BEANCOUNT_V3:
        assert "__duplicate__" not in entries[1].meta
        assert "__duplicate__" in entries[2].meta

    ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestBeangulpImporter",
    )
    snapshot([serialise(e) for e in entries], json=True)


def test_ingest_errors_file_does_not_exist(
    get_ledger: GetFavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ingest_ledger = get_ledger("import")
    ingest_ledger.ingest.load_file()
    assert not ingest_ledger.ingest.errors
    monkeypatch.setattr(
        ingest_ledger.fava_options,
        "import_config",
        "does_not_exist.py",
    )
    ingest_ledger.ingest.load_file()
    assert ingest_ledger.ingest.errors


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
