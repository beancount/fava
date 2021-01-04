"""Ingest helper functions."""
import datetime
import os
import runpy
import sys
import traceback
from os import path
from typing import List
from typing import NamedTuple
from typing import Optional

from beancount.ingest import cache  # type: ignore
from beancount.ingest import extract
from beancount.ingest import identify

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError


class IngestError(BeancountError):
    """An error with one of the importers."""


class FileImportInfo(NamedTuple):
    """Info about one file/importer combination."""

    importer_name: str
    account: str
    date: datetime.date
    name: str


class FileImporters(NamedTuple):
    """Importers for a file."""

    name: str
    basename: str
    importers: List[FileImportInfo]


def file_import_info(filename: str, importer) -> FileImportInfo:
    """Generate info about a file with an importer."""
    # pylint: disable=broad-except
    file = cache.get_file(filename)
    try:
        account = importer.file_account(file)
    except Exception:
        account = ""
    try:
        date = importer.file_date(file)
    except Exception:
        date = datetime.date.today()
    try:
        name = importer.file_name(file)
    except Exception:
        name = path.basename(filename)

    return FileImportInfo(importer.name(), account, date, name)


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.config = []
        self.importers = {}
        self.hooks = []
        self.mtime = None

    @property
    def module_path(self) -> Optional[str]:
        """The path to the importer configuration."""
        config_path = self.ledger.fava_options["import-config"]
        if not config_path:
            return None
        return self.ledger.join_path(config_path)

    def load_file(self) -> None:
        if not self.ledger.fava_options["import-config"]:
            return

        if not self.module_path:
            return

        if not path.exists(self.module_path) or path.isdir(self.module_path):
            self.ledger.errors.append(
                IngestError(
                    None,
                    f"File does not exist: '{self.module_path}'",
                    None,
                )
            )
            return

        if os.stat(self.module_path).st_mtime_ns == self.mtime:
            return

        try:
            mod = runpy.run_path(self.module_path)
        except Exception:  # pylint: disable=broad-except
            message = "".join(traceback.format_exception(*sys.exc_info()))
            self.ledger.errors.append(
                IngestError(
                    None,
                    f"Error in importer '{self.module_path}': {message}",
                    None,
                )
            )
            return

        self.mtime = os.stat(self.module_path).st_mtime_ns
        self.config = mod["CONFIG"]
        self.hooks = [extract.find_duplicate_entries]
        if "HOOKS" in mod:
            hooks = mod["HOOKS"]
            if not isinstance(hooks, list) or not all(
                callable(fn) for fn in hooks
            ):
                message = "HOOKS is not a list of callables"
                self.ledger.errors.append(
                    IngestError(
                        None,
                        f"Error in importer '{self.module_path}': {message}",
                        None,
                    )
                )
            else:
                self.hooks = hooks
        self.importers = {
            importer.name(): importer for importer in self.config
        }

    def import_data(self) -> List[FileImporters]:
        """Identify files and importers that can be imported.

        Returns:
            A list of :class:`.FileImportInfo`.
        """
        if not self.config:
            return []

        ret: List[FileImporters] = []

        for directory in self.ledger.fava_options["import-dirs"]:
            full_path = self.ledger.join_path(directory)
            files = list(identify.find_imports(self.config, full_path))
            for (filename, importers) in files:
                basename = path.basename(filename)
                infos = [
                    file_import_info(filename, importer)
                    for importer in importers
                ]
                ret.append(FileImporters(filename, basename, infos))

        return ret

    def extract(self, filename: str, importer_name: str):
        """Extract entries from filename with the specified importer.

        Args:
            filename: The full path to a file.
            importer_name: The name of an importer that matched the file.

        Returns:
            A list of new imported entries.
        """
        if (
            not filename
            or not importer_name
            or not self.config
            or not self.module_path
        ):
            return []

        if os.stat(self.module_path).st_mtime_ns > self.mtime:
            self.load_file()

        new_entries = extract.extract_from_file(
            filename,
            self.importers.get(importer_name),
            existing_entries=self.ledger.all_entries,
        )

        new_entries_list = [(filename, new_entries)]
        for hook_fn in self.hooks:
            new_entries_list = hook_fn(
                new_entries_list, self.ledger.all_entries
            )

        return new_entries_list[0][1]
