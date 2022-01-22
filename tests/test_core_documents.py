# pylint: disable=missing-docstring
from __future__ import annotations

from os import path

import pytest
from pytest import MonkeyPatch

from fava.core import FavaLedger
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.helpers import FavaAPIException


def test_is_document_or_import_file(
    example_ledger: FavaLedger, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", ["/test/"])
    assert not is_document_or_import_file("/asdfasdf", example_ledger)
    assert not is_document_or_import_file("/test/../../err", example_ledger)
    assert is_document_or_import_file("/test/err/../err", example_ledger)
    assert is_document_or_import_file("/test/err/../err", example_ledger)


def test_filepath_in_documents_folder(
    example_ledger: FavaLedger, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setitem(
        example_ledger.options, "documents", ["/test"]  # type: ignore
    )

    def _join(start: str, *args: str) -> str:
        return path.abspath(path.join(start, *args))

    assert filepath_in_document_folder(
        "/test", "Assets:US:BofA:Checking", "filename", example_ledger
    ) == _join("/test", "Assets", "US", "BofA", "Checking", "filename")
    assert filepath_in_document_folder(
        "/test", "Assets:US:BofA:Checking", "file/name", example_ledger
    ) == _join("/test", "Assets", "US", "BofA", "Checking", "file name")
    assert filepath_in_document_folder(
        "/test", "Assets:US:BofA:Checking", "/../file/name", example_ledger
    ) == _join("/test", "Assets", "US", "BofA", "Checking", " .. file name")
    with pytest.raises(FavaAPIException):
        filepath_in_document_folder(
            "/test", "notanaccount", "filename", example_ledger
        )
    with pytest.raises(FavaAPIException):
        filepath_in_document_folder(
            "/notadocumentsfolder",
            "Assets:US:BofA:Checking",
            "filename",
            example_ledger,
        )
