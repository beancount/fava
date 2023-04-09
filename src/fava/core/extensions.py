"""Fava extensions."""
from __future__ import annotations

from inspect import getfile
from os.path import dirname
from os.path import join
from typing import TYPE_CHECKING

from fava.core.module_base import FavaModule
from fava.ext import FavaExtensionBase
from fava.ext import find_extensions

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Custom
    from fava.beans.abc import Directive
    from fava.core import FavaLedger


class ExtensionModule(FavaModule):
    """Fava extensions."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self._instances: dict[type[FavaExtensionBase], FavaExtensionBase] = {}
        self.reports: list[tuple[str, str]] = []

    def load_file(self) -> None:
        all_extensions = []
        custom_entries = self.ledger.all_entries_by_type.Custom
        _extension_entries = extension_entries(custom_entries)

        for extension in _extension_entries:
            extensions, errors = find_extensions(
                dirname(self.ledger.beancount_file_path), extension
            )
            all_extensions.extend(extensions)
            self.ledger.errors.extend(errors)

        for cls in all_extensions:
            module = cls.__module__
            ext_config = (
                _extension_entries[module]
                if (module in _extension_entries)
                else None
            )
            if cls not in self._instances:
                self._instances[cls] = cls(self.ledger, ext_config)

        self.reports = [
            (ext.name, ext.report_title)
            for ext in self._instances.values()
            if ext.report_title is not None
        ]

    def exts_for_hook(self, hook: str) -> list[FavaExtensionBase]:
        """Find all extensions that have implemented the given hook."""
        return [
            ext
            for base, ext in self._instances.items()
            if getattr(base, hook) != getattr(FavaExtensionBase, hook)
        ]

    def template_and_extension(
        self, name: str
    ) -> tuple[str, FavaExtensionBase]:
        """Provide data to render an extension report.

        Args:
            name: The extension class qualname.
        Returns:
            Tuple of associated template source, extension instance
        """
        for ext_class, ext in self._instances.items():
            if ext_class.__qualname__ == name:
                extension_dir = dirname(getfile(ext_class))
                template_path = join(
                    extension_dir,
                    "templates",
                    f"{ext_class.__qualname__}.html",
                )

                with open(template_path, encoding="utf-8") as ext_template:
                    return ext_template.read(), ext

        raise LookupError("Extension report not found.")

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        for ext in self.exts_for_hook("after_entry_modified"):
            ext.after_entry_modified(entry, new_lines)

    def after_insert_entry(self, entry: Directive) -> None:
        for ext in self.exts_for_hook("after_insert_entry"):
            ext.after_insert_entry(entry)

    def after_insert_metadata(
        self, entry: Directive, key: str, value: str
    ) -> None:
        for ext in self.exts_for_hook("after_insert_metadata"):
            ext.after_insert_metadata(entry, key, value)

    def after_write_source(self, path: str, source: str) -> None:
        for ext in self.exts_for_hook("after_write_source"):
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
