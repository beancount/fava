"""Fava's import system."""

from collections import namedtuple
from enum import Enum
import importlib
import inspect
import sys


class IngestType(Enum):
    IMPORT = 1
    DUPLICATE = 2
    IGNORE = 3


FavaIngestEntry = namedtuple('FavaIngestEntry', 'line source entry type')
FavaIngestError = namedtuple('FavaIngestError', 'source message entry')


class FavaIngestBase(object):
    """Base class for ingesters for Fava.

    Any ingesters should inherit from this class. :func:`find_importer` will
    discover all subclasses of this class in the specified modules.
    """
    def __init__(self, ledger):
        self.ledger = ledger

    def run_ingest(self, *args):
        """Run ingest.

        If this method returns None, the ingester did not recognize the file
        and is not able to import it.

        Args:
            file: File-like object that should be imported.

        Returns:
            None if the file cannot be ingested. A list of
            :class:`FavaIngestEntry` if it can be ingested.
        """
        try:
            getattr(self, 'run_ingest')(*args)
        except AttributeError:
            pass


def find_ingesters(base_path, name):
    """Find ingesters in a module.

    Args:
        base_path: The module can be relative to this path.
        name: The name of the module containing the importer.

    Returns:
        A tuple (classes, errors) where classes is a list of subclasses of
        :class:`FavaIngestBase` found in ``name``.
    """
    classes = []

    sys.path.insert(0, base_path)
    try:
        module = importlib.import_module(name)
    except ImportError as e:
        return [], [FavaIngestError(
            None, 'Importing module "{}" failed.'.format(name), None)]
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, FavaIngestBase) and obj != FavaIngestBase:
            classes.append(obj)
    sys.path.pop(0)

    if not classes:
        return [], [FavaIngestError(
            None, 'Module "{}" contains no ingesters.'.format(name), None)]

    return classes, []
