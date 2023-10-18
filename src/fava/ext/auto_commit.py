"""Auto-commit hook for Fava.

This mainly serves as an example how Fava's extension systems, which only
really does hooks at the moment, works.
"""

from __future__ import annotations

from pathlib import Path
from subprocess import call
from subprocess import DEVNULL
from typing import Any
from typing import TYPE_CHECKING

from fava.ext import FavaExtensionBase

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


class AutoCommit(FavaExtensionBase):
    """Auto-commit hook for Fava."""

    def _run(self, args: list[str]) -> None:
        cwd = Path(self.ledger.beancount_file_path).parent
        call(args, cwd=cwd, stdout=DEVNULL)

    def after_write_source(self, path: str, _: Any) -> None:
        message = "autocommit: file saved"
        self._run(["git", "add", path])
        self._run(["git", "commit", "-m", message])

    def after_insert_metadata(self, *_: Any) -> None:
        message = "autocommit: metadata added"
        self._run(["git", "commit", "-am", message])

    def after_insert_entry(self, entry: Directive) -> None:
        message = f"autocommit: entry on {entry.date}"
        self._run(["git", "commit", "-am", message])

    def after_delete_entry(self, entry: Directive) -> None:
        message = f"autocommit: deleted entry on {entry.date}"
        self._run(["git", "commit", "-am", message])

    def after_entry_modified(self, entry: Directive, _: Any) -> None:
        message = f"autocommit: modified entry on {entry.date}"
        self._run(["git", "commit", "-am", message])
