"""Fava's extension system."""
from __future__ import annotations

import ast
import importlib
import inspect
import sys
from typing import Any
from typing import TYPE_CHECKING

from beancount.core.data import Directive

from fava.helpers import BeancountError

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


class FavaExtensionError(BeancountError):
    """Error in one of Fava's extensions."""


class FavaExtensionBase:
    """Base class for extensions for Fava.

    Any extension should inherit from this class. :func:`find_extension` will
    discover all subclasses of this class in the specified modules.
    """

    report_title: str | None = None

    config: Any

    def __init__(self, ledger: FavaLedger, config: str | None = None) -> None:
        """
        Base init function.

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
        self.name = self.__class__.__qualname__

    def after_entry_modified(self, entry: Directive, new_lines: str) -> None:
        """Called after an `entry` has been modified."""

    def after_insert_entry(self, entry: Directive) -> None:
        """Called after an `entry` has been inserted."""

    def after_insert_metadata(
        self, entry: Directive, key: str, value: str
    ) -> None:
        """Called after metadata (key: value) was added to an entry."""

    def after_write_source(self, path: str, source: str) -> None:
        """Called after `source` has been written to path."""


def find_extensions(
    base_path: str, name: str
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

    sys.path.insert(0, base_path)
    try:
        module = importlib.import_module(name)
    except ImportError:
        error = FavaExtensionError(
            None, f'Importing module "{name}" failed.', None
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
