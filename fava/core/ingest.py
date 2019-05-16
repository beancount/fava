"""Ingest helper functions."""

from collections import namedtuple
import datetime
from os import path
import os
import runpy
import sys
import traceback

from beancount.ingest import cache
from beancount.ingest import extract
from beancount.ingest import identify

from fava.core.helpers import FavaModule

IngestError = namedtuple("IngestError", "source message entry")

FileImporters = namedtuple("FileImporters", "name basename importers")
FileImportInfo = namedtuple(
    "FileImportInfo", "importer_name account date name"
)


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
        self.mtime = None

    @property
    def module_path(self):
        """The path to the importer configuration."""
        config_path = self.ledger.fava_options["import-config"]
        if not config_path:
            return None
        return self.ledger.join_path(config_path)

    def load_file(self):
        if not self.ledger.fava_options["import-config"]:
            return

        if not path.exists(self.module_path) or path.isdir(self.module_path):
            self.ledger.errors.append(
                IngestError(
                    None,
                    "File does not exist: '{}'".format(self.module_path),
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
                    "Error in importer '{}': {}".format(
                        str(self.module_path), message
                    ),
                    None,
                )
            )
            return

        self.mtime = os.stat(self.module_path).st_mtime_ns
        self.config = mod["CONFIG"]
        self.importers = {
            importer.name(): importer for importer in self.config
        }

    def import_data(self):
        """Identify files and importers that can be imported.

        Returns:
            A dict mapping directories to lists of :class:`.FileImportInfo`.
        """
        if not self.config:
            return {}

        ret = {}

        for directory in self.ledger.fava_options["import-dirs"]:
            full_path = self.ledger.join_path(directory)
            files = list(identify.find_imports(self.config, full_path))
            ret[directory] = []
            for (filename, importers) in files:
                basename = path.basename(filename)
                infos = [
                    file_import_info(filename, importer)
                    for importer in importers
                ]
                ret[directory].append(FileImporters(filename, basename, infos))

        return ret

    def extract(self, filename, importer_name):
        """Extract entries from filename with the specified importer.

        Args:
            filename: The full path to a file.
            importer_name: The name of an importer that matched the file.

        Returns:
            A list of new imported entries.
        """
        if not filename or not importer_name or not self.config:
            return []

        if os.stat(self.module_path).st_mtime_ns > self.mtime:
            self.load_file()

        new_entries = extract.extract_from_file(
            filename,
            self.importers.get(importer_name),
            existing_entries=self.ledger.all_entries,
        )

        new_entries = extract.find_duplicate_entries(
            [(filename, new_entries)], self.ledger.all_entries
        )[0][1]

        return new_entries
