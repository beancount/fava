# pylint: disable=missing-docstring,unused-argument,multiple-statements
from beancount.core.data import Directive

def parse_string(string: str) -> tuple[list[Directive], None, None]: ...
