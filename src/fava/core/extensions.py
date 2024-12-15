"""Fava extensions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.ext import ExtensionConfigError
from fava.ext import FavaExtensionError
from fava.ext import find_extensions

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Sequence

    from fava.beans.abc import Directive
    from fava.core import FavaLedger
    from fava.ext import FavaExtensionBase


@dataclass
class ExtensionDetails:
    """The information about an extension that is needed for the frontend."""

    name: str
    report_title: str | None
    has_js_module: bool


class ExtensionModule(FavaModule):
    """Fava extensions."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self._instances: dict[str, FavaExtensionBase] = {}
        self._loaded_extensions: set[type[FavaExtensionBase]] = set()
        self.errors: list[FavaExtensionError] = []

    def load_file(self) -> None:  # noqa: D102
        self.errors = []

        custom_entries = self.ledger.all_entries_by_type.Custom

        seen = set()
        for entry in (e for e in custom_entries if e.type == "fava-extension"):
            extension = entry.values[0].value
            if extension in seen:  # pragma: no cover
                self.errors.append(
                    FavaExtensionError(
                        entry.meta, f"Duplicate extension '{extension}'", entry
                    )
                )
                continue

            seen.add(extension)
            extensions, errors = find_extensions(
                Path(self.ledger.beancount_file_path).parent,
                extension,
            )
            self.errors.extend(errors)

            for cls in extensions:
                ext_config = (
                    entry.values[1].value if len(entry.values) > 1 else None
                )
                if cls not in self._loaded_extensions:
                    self._loaded_extensions.add(cls)
                    try:
                        ext = cls(self.ledger, ext_config)
                        self._instances[ext.name] = ext
                    except ExtensionConfigError as error:  # pragma: no cover
                        self.errors.append(
                            FavaExtensionError(entry.meta, str(error), entry)
                        )

    @property
    def _exts(self) -> Iterable[FavaExtensionBase]:
        return self._instances.values()

    @property
    def extension_details(self) -> Sequence[ExtensionDetails]:
        """Extension information to provide to the Frontend."""
        return [
            ExtensionDetails(ext.name, ext.report_title, ext.has_js_module)
            for ext in self._exts
        ]

    def get_extension(self, name: str) -> FavaExtensionBase | None:
        """Get the extension with the given name."""
        return self._instances.get(name, None)

    def after_load_file(self) -> None:
        """Run all `after_load_file` hooks."""
        for ext in self._exts:
            ext.after_load_file()

    def before_request(self) -> None:
        """Run all `before_request` hooks."""
        for ext in self._exts:
            ext.before_request()

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        """Run all `after_entry_modified` hooks."""
        for ext in self._exts:
            ext.after_entry_modified(entry, new_lines)

    def after_insert_entry(self, entry: Directive) -> None:
        """Run all `after_insert_entry` hooks."""
        for ext in self._exts:
            ext.after_insert_entry(entry)

    def after_delete_entry(self, entry: Directive) -> None:
        """Run all `after_delete_entry` hooks."""
        for ext in self._exts:
            ext.after_delete_entry(entry)

    def after_insert_metadata(
        self,
        entry: Directive,
        key: str,
        value: str,
    ) -> None:
        """Run all `after_insert_metadata` hooks."""
        for ext in self._exts:
            ext.after_insert_metadata(entry, key, value)

    def after_write_source(self, path: str, source: str) -> None:
        """Run all `after_write_source` hooks."""
        for ext in self._exts:
            ext.after_write_source(path, source)
