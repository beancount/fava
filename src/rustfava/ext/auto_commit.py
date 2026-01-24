"""Auto-commit hook for rustfava.

This mainly serves as an example how rustfava's extension systems, which only
really does hooks at the moment, works.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from typing import override

from rustfava.ext import RustfavaExtensionBase

if TYPE_CHECKING:  # pragma: no cover
    from rustfava.beans.abc import Directive


class AutoCommit(RustfavaExtensionBase):  # pragma: no cover
    """Auto-commit hook for rustfava."""

    def _run(self, args: list[str]) -> None:
        cwd = Path(self.ledger.beancount_file_path).parent
        subprocess.run(args, cwd=cwd, stdout=subprocess.DEVNULL, check=False)

    @override
    def after_write_source(self, path: str, source: str) -> None:
        """Add changed file to git and commit."""
        message = "autocommit: file saved"
        self._run(["git", "add", path])
        self._run(["git", "commit", "-m", message])

    @override
    def after_insert_metadata(
        self,
        entry: Directive,
        key: str,
        value: str,
    ) -> None:
        """Commit all changes on `after_insert_metadata`."""
        message = "autocommit: metadata added"
        self._run(["git", "commit", "-am", message])

    @override
    def after_insert_entry(self, entry: Directive) -> None:
        """Commit all changes on `after_insert_entry`."""
        message = f"autocommit: entry on {entry.date}"
        self._run(["git", "commit", "-am", message])

    @override
    def after_delete_entry(self, entry: Directive) -> None:
        """Commit all changes on `after_delete_entry`."""
        message = f"autocommit: deleted entry on {entry.date}"
        self._run(["git", "commit", "-am", message])

    @override
    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        """Commit all changes on `after_entry_modified`."""
        message = f"autocommit: modified entry on {entry.date}"
        self._run(["git", "commit", "-am", message])
