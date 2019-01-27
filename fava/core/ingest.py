"""Ingest helper functions."""

import operator
import os
from os import path
import runpy
from collections import namedtuple
import sys
import traceback

from beancount.ingest import cache, identify, extract

from fava.core.helpers import FavaModule

IngestError = namedtuple("IngestError", "source message entry")


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
        if not self.ledger.fava_options["import-config"]:
            return None
        return path.normpath(
            path.join(
                path.dirname(self.ledger.beancount_file_path),
                self.ledger.fava_options["import-config"],
            )
        )

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

    def identify_directory(self, directory):
        """Identify files and importers for a given directory.

        Args:
            directory: The directory to search (relative to Beancount file).

        Returns:
            Tuples of filenames and lists of matching importers.
        """
        if not self.config:
            return []

        full_path = path.normpath(
            path.join(path.dirname(self.ledger.beancount_file_path), directory)
        )

        return filter(
            operator.itemgetter(1),
            identify.find_imports(self.config, full_path),
        )

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

        if isinstance(new_entries, tuple):
            new_entries, _ = new_entries

        return new_entries

    @staticmethod
    def file_account(filename, importer):
        """Account for the given file.

        Args:
            filename: The full path to a file.
            importer: An importer that matched the file.

        Returns:
            The account name or the exception message if one occurs.
        """
        try:
            return importer.file_account(cache.get_file(filename))
        except Exception as exception:  # pylint: disable=broad-except
            return str(exception)

    @staticmethod
    def file_date(filename, importer):
        """Date for the given file.

        Args:
            filename: The full path to a file.
            importer: An importer that matched the file.

        Returns:
            The date or the exception message if one occurs.
        """
        try:
            return importer.file_date(cache.get_file(filename))
        except Exception as exception:  # pylint: disable=broad-except
            return str(exception)
