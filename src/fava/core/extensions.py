"""Fava extensions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.ext import find_extensions

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Custom
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

    def load_file(self) -> None:
        all_extensions = []
        custom_entries = self.ledger.all_entries_by_type.Custom
        _extension_entries = extension_entries(custom_entries)

        for extension in _extension_entries:
            extensions, errors = find_extensions(
                Path(self.ledger.beancount_file_path).parent,
                extension,
            )
            all_extensions.extend(extensions)
            self.ledger.errors.extend(errors)

        for cls in all_extensions:
            module = cls.__module__
            ext_config = _extension_entries.get(module, None)
            if cls not in self._loaded_extensions:
                self._loaded_extensions.add(cls)
                ext = cls(self.ledger, ext_config)
                self._instances[ext.name] = ext

    @property
    def _exts(self) -> list[FavaExtensionBase]:
        return list(self._instances.values())

    @property
    def extension_details(self) -> list[ExtensionDetails]:
        """Extension information to provide to the Frontend."""
        return [
            ExtensionDetails(ext.name, ext.report_title, ext.has_js_module)
            for ext in self._exts
        ]

    def get_extension(self, name: str) -> FavaExtensionBase | None:
        """Get the extension with the given name."""
        return self._instances.get(name, None)

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        for ext in self._exts:
            ext.after_entry_modified(entry, new_lines)

    def after_insert_entry(self, entry: Directive) -> None:
        for ext in self._exts:
            ext.after_insert_entry(entry)

    def after_delete_entry(self, entry: Directive) -> None:
        for ext in self._exts:
            ext.after_delete_entry(entry)

    def after_insert_metadata(
        self,
        entry: Directive,
        key: str,
        value: str,
    ) -> None:
        for ext in self._exts:
            ext.after_insert_metadata(entry, key, value)

    def after_write_source(self, path: str, source: str) -> None:
        for ext in self._exts:
            ext.after_write_source(path, source)


def extension_entries(
    custom_entries: list[Custom],
) -> dict[str, str | None]:
    """Parse custom entries for extensions.

    They have the following format::

        2016-04-01 custom "fava-extension" "my_extension" "{'my_option': {}}"
    """
    _extension_entries = [
        entry for entry in custom_entries if entry.type == "fava-extension"
    ]
    return {
        entry.values[0].value: (
            entry.values[1].value if (len(entry.values) == 2) else None
        )
        for entry in _extension_entries
    }
