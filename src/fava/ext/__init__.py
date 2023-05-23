"""Fava's extension system."""
from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

from fava.helpers import BeancountError

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.core import FavaLedger


class FavaExtensionError(BeancountError):
    """Error in one of Fava's extensions."""


class FavaExtensionBase:
    """Base class for extensions for Fava.

    Any extension should inherit from this class. :func:`find_extension` will
    discover all subclasses of this class in the specified modules.
    """

    #: Name for a HTML report for this extension.
    report_title: str | None = None

    #: Whether this extension includes a Javascript module.
    has_js_module: bool = False

    config: Any

    def __init__(self, ledger: FavaLedger, config: str | None = None) -> None:
        """Initialise extension.

        Args:
            ledger: Input ledger file.
            config: Configuration options string passed from the
                    beancount file's 'fava-extension' line.
        """
        self.ledger = ledger
        try:
            self.config = ast.literal_eval(config) if config else None
        except ValueError:
            self.config = None

    @property
    def name(self) -> str:
        """Unique name of this extension."""
        return self.__class__.__qualname__

    @property
    def extension_dir(self) -> Path:
        """Directory to look for templates directory and Javascript code."""
        return Path(inspect.getfile(self.__class__)).parent

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        """Run after an `entry` has been modified."""

    def after_insert_entry(self, entry: Directive) -> None:
        """Run after an `entry` has been inserted."""

    def after_insert_metadata(
        self, entry: Directive, key: str, value: str
    ) -> None:
        """Run after metadata (key: value) was added to an entry."""

    def after_write_source(self, path: str, source: str) -> None:
        """Run after `source` has been written to path."""


def find_extensions(
    base_path: Path, name: str
) -> tuple[list[type[FavaExtensionBase]], list[FavaExtensionError]]:
    """Find extensions in a module.

    Args:
        base_path: The module can be relative to this path.
        name: The name of the module containing the extensions.

    Returns:
        A tuple (classes, errors) where classes is a list of subclasses of
        :class:`FavaExtensionBase` found in ``name``.
    """
    classes = []

    sys.path.insert(0, str(base_path))
    try:
        module = importlib.import_module(name)
    except ImportError as err:
        error = FavaExtensionError(
            None,
            f'Importing module "{name}" failed.\nError: "{err.msg}"',
            None,
        )
        return (
            [],
            [error],
        )
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, FavaExtensionBase) and obj != FavaExtensionBase:
            classes.append(obj)
    sys.path.pop(0)

    if not classes:
        error = FavaExtensionError(
            None,
            f'Module "{name}" contains no extensions.',
            None,
        )
        return (
            [],
            [error],
        )

    return classes, []
