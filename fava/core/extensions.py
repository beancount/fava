"""Fava extensions """

import os
import inspect

from beancount.core.data import Custom

from fava.core.helpers import FavaModule
from fava.ext import find_extensions


# pylint: disable=missing-docstring
class ExtensionModule(FavaModule):
    """Some attributes of the ledger (mostly for auto-completion)."""

    def __init__(self, ledger):
        super().__init__(ledger)
        self._extensions = None
        self._instances = {}
        self.active_ext = None

    def load_file(self):
        self._extensions = []
        custom_entries = self.ledger.all_entries_by_type[Custom]
        _extension_entries = extension_entries(custom_entries)

        for extension in _extension_entries:
            extensions, errors = find_extensions(
                os.path.dirname(self.ledger.beancount_file_path), extension
            )
            self._extensions.extend(extensions)
            self.ledger.errors.extend(errors)

        for cls in self._extensions:
            module = cls.__module__
            ext_config = (
                _extension_entries[module]
                if (module in _extension_entries)
                else None
            )
            if cls not in self._instances:
                self._instances[cls] = cls(self.ledger, ext_config)

    def run_hook(self, event, *args):
        for ext in self._instances.values():
            ext.run_hook(event, *args)

    def report_attributes(self):
        """Returns report-specific attributes for use by views.

        Returns:
            A tuple of attributes (name, title)
        """
        attributes = []
        for ext_class in self._instances:
            ext = self._instances[ext_class]
            if report_template_path(ext_class) is not None:
                if hasattr(ext, "report_title"):
                    attributes.append((ext.name, ext.report_title))
                else:
                    attributes.append((ext.name, ext.name))
        return attributes

    def report_template_data(self, name):
        # pylint: disable=no-self-use
        """Provide data to render an extension report.

        Args:
            name: The extension class qualname.
        Returns:
            Tuple of associated template source, extension instance
        """
        for ext_class in self._instances:
            if ext_class.__qualname__ == name:
                template_path = report_template_path(ext_class)
                if template_path is None:
                    continue

                with open(template_path) as ext_template:
                    return ext_template.read(), self._instances[ext_class]

        raise LookupError("Extension report not found.")

    def report_page_globals(self):
        """Create page globals for extensions.

        Args: A FavaLedger ExtensionModule object.

        Returns: Array of tupled globals to be appended to all_pages.
        """
        report_attributes = self.report_attributes()
        page_globals = list(map(lambda x: (x[0], x[1], ""), report_attributes))
        return page_globals


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


def report_template_path(ext_class):
    """Template path for extension report.

        Args:
            class: Extension class
        Returns: String path or None.
    """
    extension_dir = os.path.dirname(inspect.getfile(ext_class))
    template_path = os.path.join(
        extension_dir, "templates", "{}.html".format(ext_class.__module__)
    )
    if os.path.isfile(template_path):
        return template_path
    return None
