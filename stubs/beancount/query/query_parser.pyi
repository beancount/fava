# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import NamedTuple

class ParseError(Exception): ...

class RunCustom(NamedTuple):
    query_name: str
