from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.beans import create
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.core.group_entries import group_entries_by_type
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def test_is_document_or_import_file(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = str(Path(__file__))
    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", ["/test/"])
    monkeypatch.setattr(
        example_ledger,
        "all_entries_by_type",
        group_entries_by_type([
            create.document({}, datetime.date(2022, 1, 1), "Assets", path)
        ]),
    )
    assert not is_document_or_import_file("/asdfasdf", example_ledger)
    assert not is_document_or_import_file("/test/../../err", example_ledger)
    assert is_document_or_import_file(path, example_ledger)
    assert is_document_or_import_file("/test/err/../err", example_ledger)
    assert is_document_or_import_file("/test/err/../err", example_ledger)


def test_filepath_in_documents_folder(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(example_ledger.options, "documents", ["/test"])

    def _join(start: str, *args: str) -> Path:
        return Path(start).joinpath(*args).resolve()

    assert filepath_in_document_folder(
        "/test",
        "Assets:US:BofA:Checking",
        "filename",
        example_ledger,
    ) == _join("/test", "Assets", "US", "BofA", "Checking", "filename")
    assert filepath_in_document_folder(
        "/test",
        "Assets:US:BofA:Checking",
        "file/name",
        example_ledger,
    ) == _join("/test", "Assets", "US", "BofA", "Checking", "file name")
    assert filepath_in_document_folder(
        "/test",
        "Assets:US:BofA:Checking",
        "/../file/name",
        example_ledger,
    ) == _join("/test", "Assets", "US", "BofA", "Checking", " .. file name")
    with pytest.raises(FavaAPIError):
        filepath_in_document_folder(
            "/test",
            "notanaccount",
            "filename",
            example_ledger,
        )
    with pytest.raises(FavaAPIError):
        filepath_in_document_folder(
            "/notadocumentsfolder",
            "Assets:US:BofA:Checking",
            "filename",
            example_ledger,
        )
