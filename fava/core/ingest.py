"""Ingest helper functions."""

import os
import runpy
import tempfile
from collections import namedtuple

from beancount.core import data
from beancount.ingest import identify, cache, extract

from fava.core.helpers import FavaModule

IngestError = namedtuple('IngestError', 'source message entry')


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self.config = None
        self.ingest_dirs = []
        self.uploaded_files = []

    def load_file(self):
        configpath = self.ledger.fava_options['ingest-config']
        if configpath:
            self.ingest_dirs = self.ledger.fava_options['ingest-dirs']

            if not os.path.exists(configpath) or os.path.isdir(configpath):
                error = IngestError(None, "File does not exist: '{}'".format(
                    configpath), None)
                self.ledger.errors.append(error)

            mod = runpy.run_path(configpath)
            self.config = mod['CONFIG']

    def _identify_importers(self, file_or_dir):
        """Identify possible importers for the specified file or directory."""
        if not self.config:
            return []

        identified = []
        files = identify.find_imports(self.config, file_or_dir)
        for filename, importers in files:
            file = cache.get_file(filename)
            if len(importers):
                identified.append({
                    'filename': filename,
                    'importers': [{
                        'name': importer.name(),
                        'account': importer.file_account(file)
                    } if importer else '-' for importer in importers]
                })

        return identified

    def add_upload(self, file):
        """Store the file in a temporary directory."""
        new_file = os.path.join(tempfile.mkdtemp(), file.filename)
        file.save(new_file)
        self.uploaded_files.append(new_file)

    def remove_upload(self, filepath):
        """Remove filepath from disk."""
        if filepath in self.uploaded_files:
            os.remove(filepath)
            self.uploaded_files.remove(filepath)

    def dirs_importers(self):
        """Return identified files and importers, grouped by directory."""
        return [(dir_, self._identify_importers(dir_))
                for dir_ in self.ingest_dirs]

    def uploads_importers(self):
        """Return identified files and importers from uploads."""
        return self._identify_importers(self.uploaded_files)

    def extract(self, filepath, importer_name):
        """Extract entries from filepath with the specified importer."""
        importer = next(
            imp for imp in self.config if imp.name() == importer_name)

        new_entries, duplicate_entries = extract.extract_from_file(
            filepath,
            importer,
            existing_entries=self.ledger.entries,
            min_date=None,
            allow_none_for_tags_and_links=False)

        entries = new_entries + duplicate_entries
        # TODO mark duplicates
        entries.sort(key=data.entry_sortkey)
        return entries
