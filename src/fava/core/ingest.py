"""Ingest helper functions."""

from __future__ import annotations

import datetime
import sys
import traceback
from dataclasses import dataclass
from os import altsep
from os import sep
from pathlib import Path
from runpy import run_path
from typing import Any
from typing import TYPE_CHECKING

from beancount.ingest import cache  # type: ignore[import-untyped]
from beancount.ingest import extract
from beancount.ingest import identify

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.core import FavaLedger


class IngestError(BeancountError):
    """An error with one of the importers."""


@dataclass(frozen=True)
class FileImportInfo:
    """Info about one file/importer combination."""

    importer_name: str
    account: str
    date: datetime.date
    name: str


@dataclass(frozen=True)
class FileImporters:
    """Importers for a file."""

    name: str
    basename: str
    importers: list[FileImportInfo]


def file_import_info(filename: str, importer: Any) -> FileImportInfo:
    """Generate info about a file with an importer."""
    file = cache.get_file(filename)
    try:
        account = importer.file_account(file)
        date = importer.file_date(file)
        name = importer.file_name(file)
    except Exception as err:  # noqa: BLE001
        raise FavaAPIError(f"Error calling importer method: {err}") from err

    return FileImportInfo(
        importer.name(),
        account or "",
        date or datetime.date.today(),
        name or Path(filename).name,
    )


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.config: list[Any] = []
        self.importers: dict[str, Any] = {}
        self.hooks: list[Any] = []
        self.mtime: int | None = None

    @property
    def module_path(self) -> Path | None:
        """The path to the importer configuration."""
        config_path = self.ledger.fava_options.import_config
        if not config_path:
            return None
        return self.ledger.join_path(config_path)

    def _error(self, msg: str) -> None:
        self.ledger.errors.append(IngestError(None, msg, None))

    def load_file(self) -> None:
        if self.module_path is None:
            return
        module_path = self.module_path

        if not module_path.exists() or module_path.is_dir():
            self._error(f"File does not exist: '{module_path}'")
            return

        if module_path.stat().st_mtime_ns == self.mtime:
            return

        try:
            mod = run_path(str(self.module_path))
        except Exception:  # noqa: BLE001
            message = "".join(traceback.format_exception(*sys.exc_info()))
            self._error(f"Error in importer '{module_path}': {message}")
            return

        self.mtime = module_path.stat().st_mtime_ns
        self.config = mod["CONFIG"]
        self.hooks = [extract.find_duplicate_entries]
        if "HOOKS" in mod:
            hooks = mod["HOOKS"]
            if not isinstance(hooks, list) or not all(
                callable(fn) for fn in hooks
            ):
                message = "HOOKS is not a list of callables"
                self._error(f"Error in importer '{module_path}': {message}")
            else:
                self.hooks = hooks
        self.importers = {
            importer.name(): importer for importer in self.config
        }

    def import_data(self) -> list[FileImporters]:
        """Identify files and importers that can be imported.

        Returns:
            A list of :class:`.FileImportInfo`.
        """
        if not self.config:
            return []

        ret: list[FileImporters] = []

        for directory in self.ledger.fava_options.import_dirs:
            full_path = self.ledger.join_path(directory)
            files = list(identify.find_imports(self.config, str(full_path)))
            for filename, importers in files:
                base = Path(filename).name
                infos = [
                    file_import_info(filename, importer)
                    for importer in importers
                ]
                ret.append(FileImporters(filename, base, infos))

        return ret

    def extract(self, filename: str, importer_name: str) -> list[Directive]:
        """Extract entries from filename with the specified importer.

        Args:
            filename: The full path to a file.
            importer_name: The name of an importer that matched the file.

        Returns:
            A list of new imported entries.
        """
        if not self.module_path:
            raise FavaAPIError("Missing import-config option")

        if (
            self.mtime is None
            or self.module_path.stat().st_mtime_ns > self.mtime
        ):
            self.load_file()

        new_entries = extract.extract_from_file(
            filename,
            self.importers.get(importer_name),
            existing_entries=self.ledger.all_entries,
        )

        new_entries_list: list[tuple[str, list[Directive]]] = [
            (filename, new_entries),
        ]
        for hook_fn in self.hooks:
            new_entries_list = hook_fn(
                new_entries_list,
                self.ledger.all_entries,
            )

        return new_entries_list[0][1]


def filepath_in_primary_imports_folder(
    filename: str,
    ledger: FavaLedger,
) -> Path:
    """File path for a document to upload to the primary import folder.

    Args:
        filename: The filename of the document.
        ledger: The FavaLedger.

    Returns:
        The path that the document should be saved at.
    """
    primary_imports_folder = next(iter(ledger.fava_options.import_dirs), None)
    if primary_imports_folder is None:
        raise FavaAPIError("You need to set at least one imports-dir.")

    for separator in sep, altsep:
        if separator:
            filename = filename.replace(separator, " ")

    return ledger.join_path(primary_imports_folder, filename)
