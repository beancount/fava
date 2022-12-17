"""Auto-commit hook for Fava.

This mainly serves as an example how Fava's extension systems, which only
really does hooks at the moment, works.
"""
# mypy: ignore-errors
# pylint: disable=missing-docstring
from __future__ import annotations

from os.path import dirname
from subprocess import call
from subprocess import DEVNULL

from fava.ext import FavaExtensionBase


class AutoCommit(FavaExtensionBase):
    """Auto-commit hook for Fava."""

    def _run(self, args):
        cwd = dirname(self.ledger.beancount_file_path)
        call(args, cwd=cwd, stdout=DEVNULL)

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
