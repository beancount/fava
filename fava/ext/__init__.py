"""Fava's extension system."""

from collections import namedtuple
import importlib
import inspect
import sys
import ast


FavaExtensionError = namedtuple("FavaExtensionError", "source message entry")


class FavaExtensionBase:
    """Base class for extensions for Fava.

    Any extension should inherit from this class. :func:`find_extension` will
    discover all subclasses of this class in the specified modules.
    """

    def __init__(self, ledger, config=None):
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

    def run_hook(self, event, *args):
        """Run a hook.

        Args:
            event: One of the possible events.

        """
        try:
            getattr(self, event)(*args)
        except AttributeError:
            pass


def find_extensions(base_path, name):
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
        return (
            [],
            [
                FavaExtensionError(
                    None, 'Importing module "{}" failed.'.format(name), None
                )
            ],
        )
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, FavaExtensionBase) and obj != FavaExtensionBase:
            classes.append(obj)
    sys.path.pop(0)

    if not classes:
        return (
            [],
            [
                FavaExtensionError(
                    None,
                    'Module "{}" contains no extensions.'.format(name),
                    None,
                )
            ],
        )

    return classes, []
