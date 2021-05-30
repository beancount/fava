# pylint: disable=missing-docstring,unused-argument,multiple-statements

from beancount.core.data import Entries
from fava.util.typing import BeancountOptions

def execute_query(
    query: str, entries: Entries, options_map: BeancountOptions
): ...
