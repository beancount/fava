# pylint: disable=missing-docstring
from __future__ import annotations

import datetime
from os import path
from typing import Any

import pytest
from beancount.core.amount import Amount
from beancount.core.data import Note
from beancount.core.data import Transaction
from beancount.ingest.importer import ImporterProtocol  # type: ignore
from pytest import MonkeyPatch

from fava.core import FavaLedger
from fava.core.ingest import file_import_info
from fava.core.ingest import FileImportInfo
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.helpers import FavaAPIException

from .conftest import data_file

FILE_PATH = data_file("import.beancount")
EXAMPLE = data_file("import.csv")


class Imp(ImporterProtocol):  # type: ignore
    def __init__(self, acc: str) -> None:
        self.acc = acc

    def name(self) -> str:
        return self.acc

    def identify(self, file: Any) -> bool:
        return self.acc in file.name


class Invalid(ImporterProtocol):  # type: ignore
    def __init__(self, acc: str) -> None:
        self.acc = acc

    def name(self) -> str:
        return self.acc

    def identify(self, file: Any) -> bool:
        return self.acc in file.name

    def file_account(self, file: Any) -> bool:
        raise ValueError("Some error reason...")


def test_ingest_file_import_info() -> None:
    ingest_ledger = FavaLedger(FILE_PATH)
    importer = next(iter(ingest_ledger.ingest.importers.values()))
    assert importer

    info = file_import_info(EXAMPLE, importer)
    assert info.account == "Assets:Checking"

    info2 = file_import_info("/asdf/basename", Imp("rawfile"))
    assert isinstance(info2.account, str)
    assert info2 == FileImportInfo(
        "rawfile", "", datetime.date.today(), "basename"
    )

    with pytest.raises(FavaAPIException) as err:
        file_import_info("/asdf/basename", Invalid("rawfile"))
    assert "Some error reason..." in err.value.message


def test_ingest_examplefile() -> None:
    ingest_ledger = FavaLedger(FILE_PATH)

    entries = ingest_ledger.ingest.extract(EXAMPLE, "<run_path>.TestImporter")
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
    example_ledger: FavaLedger, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", ["/test"])

    def _join(start: str, *args: str) -> str:
        return path.abspath(path.join(start, *args))

    assert filepath_in_primary_imports_folder(
        "filename", example_ledger
    ) == _join("/test", "filename")
    assert filepath_in_primary_imports_folder(
        "file/name", example_ledger
    ) == _join("/test", "file name")
    assert filepath_in_primary_imports_folder(
        "/../file/name", example_ledger
    ) == _join("/test", " .. file name")

    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", [])
    with pytest.raises(FavaAPIException):
        filepath_in_primary_imports_folder("filename", example_ledger)
