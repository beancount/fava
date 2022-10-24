# pylint: disable=missing-docstring,unused-argument,multiple-statements
from beancount.core.data import Entries

def parse_string(string: str) -> tuple[Entries, None, None]: ...
