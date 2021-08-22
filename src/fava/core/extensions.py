"""Fava extensions"""
import inspect
import os
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type

from beancount.core.data import Custom

from fava.core.module_base import FavaModule
from fava.ext import FavaExtensionBase
from fava.ext import find_extensions


class ExtensionModule(FavaModule):
    """Fava extensions."""

    def __init__(self, ledger) -> None:
        super().__init__(ledger)
        self._instances: Dict[Type[FavaExtensionBase], FavaExtensionBase] = {}
        self.reports: List[Tuple[str, str]] = []

    def load_file(self) -> None:
        all_extensions = []
        custom_entries = self.ledger.all_entries_by_type[Custom]
        _extension_entries = extension_entries(custom_entries)

        for extension in _extension_entries:
            extensions, errors = find_extensions(
                os.path.dirname(self.ledger.beancount_file_path), extension
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

        self.reports = []
        for ext_class in self._instances:
            ext = self._instances[ext_class]
            if ext.report_title is not None:
                self.reports.append((ext.name, ext.report_title))

    def run_hook(self, event: str, *args) -> None:
        """Run a hook for all extensions."""
        for ext in self._instances.values():
            ext.run_hook(event, *args)

    def template_and_extension(
        self, name: str
    ) -> Tuple[str, FavaExtensionBase]:
        """Provide data to render an extension report.

        Args:
            name: The extension class qualname.
        Returns:
            Tuple of associated template source, extension instance
        """
        for ext_class in self._instances:
            if ext_class.__qualname__ == name:
                extension_dir = os.path.dirname(inspect.getfile(ext_class))
                template_path = os.path.join(
                    extension_dir,
                    "templates",
                    f"{ext_class.__qualname__}.html",
                )

                with open(template_path) as ext_template:
                    return ext_template.read(), self._instances[ext_class]

        raise LookupError("Extension report not found.")


def extension_entries(custom_entries):
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
