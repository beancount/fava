from typing import NamedTuple

class ParseError(Exception): ...

class RunCustom(NamedTuple):
    query_name: str
