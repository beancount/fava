"""Fava extensions"""

import os
import inspect

from beancount.core.data import Custom

from fava.core.helpers import FavaModule
from fava.ext import find_extensions


class ExtensionModule(FavaModule):
    """Fava extensions."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self._instances = {}
        self.reports = []

    def load_file(self):
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
            if hasattr(ext, "report_title"):
                self.reports.append((ext.name, ext.report_title))

    def run_hook(self, event, *args):
        """Run a hook for all extensions."""
        for ext in self._instances.values():
            ext.run_hook(event, *args)

    def template_and_extension(self, name):
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
                    "{}.html".format(ext_class.__qualname__),
                )

                with open(template_path) as ext_template:
                    return ext_template.read(), self._instances[ext_class]

        raise LookupError("Extension report not found.")


def extension_entries(custom_entries):
    """Parse custom entries for extensions.

    They have the following format:
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
