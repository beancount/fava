"""Ingest helper functions."""

import operator
import os
import runpy
from collections import namedtuple

from beancount.ingest import identify, extract

from fava.core.helpers import FavaModule

IngestError = namedtuple('IngestError', 'source message entry')


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.config = []

    def load_file(self):
        if self.ledger.fava_options['import-config']:
            full_path = os.path.normpath(
                os.path.join(
                    os.path.dirname(self.ledger.beancount_file_path),
                    self.ledger.fava_options['import-config']))

            if not os.path.exists(full_path) or os.path.isdir(full_path):
                error = IngestError(
                    None, "File does not exist: '{}'".format(full_path), None)
                self.ledger.errors.append(error)
            else:
                mod = runpy.run_path(full_path)
                self.config = mod['CONFIG']

    def identify_directory(self, directory):
        """Identify files and importers for a given directory.

        Args:
            directory: The directory to search (relative to Beancount file).

        Returns:
            Tuples of filenames and lists of matching importers.
        """
        if not self.config:
            return []

        full_path = os.path.normpath(
            os.path.join(
                os.path.dirname(self.ledger.beancount_file_path),
                directory))

        return filter(
            operator.itemgetter(1),
            identify.find_imports(self.config, full_path))

    def extract(self, filepath, importer_name):
        """Extract entries from filepath with the specified importer."""
        importer = next(imp for imp in self.config
                        if imp.name() == importer_name)

        new_entries, _ = extract.extract_from_file(
            filepath, importer, existing_entries=self.ledger.all_entries)

        return new_entries
