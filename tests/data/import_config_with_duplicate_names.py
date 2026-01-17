"""Test importer config having multiple importers with same name."""

from __future__ import annotations

from pathlib import Path

from beangulp import Importer

try:
    from typing import override
except ImportError:
    from typing_extensions import override


class TestImporter(Importer):
    """Simple importer using string in filename to distinguish accounts."""

    def __init__(self, account: str, file_id: str) -> None:
        self._account = account
        self._file_id = file_id

    @override
    def identify(self, filepath: str) -> bool:
        return self._file_id in Path(filepath).name

    @override
    def account(self, filepath: str) -> str:
        return self._account


CONFIG: list[Importer] = [
    TestImporter(account="Assets:Checking", file_id="1111"),
    TestImporter(account="Assets:Savings", file_id="8888"),
]
