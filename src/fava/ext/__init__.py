"""Fava's extension system."""
import ast
import importlib
import inspect
import sys
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from fava.helpers import BeancountError


class FavaExtensionError(BeancountError):
    """Error in one of Fava's extensions."""


class FavaExtensionBase:
    """Base class for extensions for Fava.

    Any extension should inherit from this class. :func:`find_extension` will
    discover all subclasses of this class in the specified modules.
    """

    report_title: Optional[str] = None

    def __init__(self, ledger, config=None) -> None:
        """
        Base init function.

        Args:
            ledger: Input ledger file.
            config: Configuration options string passed from the
                    beancount file's 'fava-extension' line.
        """
        self.ledger = ledger
        try:
            self.config = ast.literal_eval(config)
        except ValueError:
            self.config = None
        self.name = self.__class__.__qualname__

    def run_hook(self, event, *args) -> None:
        """Run a hook.

        Args:
            event: One of the possible events.
        """
        try:
            getattr(self, event)(*args)
        except AttributeError:
            pass


def find_extensions(
    base_path: str, name: str
) -> Tuple[List[Type[FavaExtensionBase]], List[FavaExtensionError]]:
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
