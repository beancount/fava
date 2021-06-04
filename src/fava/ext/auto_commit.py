"""Auto-commit hook for Fava.

This mainly serves as an example how Fava's extension systems, which only
really does hooks at the moment, works.
"""
# mypy: ignore-errors
# pylint: disable=missing-docstring
# pragma: no cover - this is just an untested example
import os
import subprocess

from fava.ext import FavaExtensionBase


class AutoCommit(FavaExtensionBase):
    def _run(self, args):
        cwd = os.path.dirname(self.ledger.beancount_file_path)
        subprocess.call(args, cwd=cwd, stdout=subprocess.DEVNULL)

    def after_write_source(self, path, _):
        message = "autocommit: file saved"
        self._run(["git", "add", path])
        self._run(["git", "commit", "-m", message])

    def after_insert_metadata(self, *_):
        message = "autocommit: metadata added"
        self._run(["git", "commit", "-am", message])

    def after_insert_entry(self, entry):
        message = f"autocommit: entry on {entry.date}"
        self._run(["git", "commit", "-am", message])

    def after_entry_modified(self, entry, _):
        message = f"autocommit: modified entry on {entry.date}"
        self._run(["git", "commit", "-am", message])
