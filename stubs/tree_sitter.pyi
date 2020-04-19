from typing import List
from typing import Optional
from typing import Tuple

Position = Tuple[int, int]

class Node:
    type: str
    is_named: bool
    start_point: Position
    start_byte: int
    end_byte: int
    children: List["Node"]
    def child_by_field_name(self, name: str) -> Optional["Node"]: ...
    def sexp(self) -> str: ...

class Tree:
    root_node: Node

class Language:
    def __init__(self, path: str, name: str) -> None: ...

class Parser:
    def set_language(self, lang: Language) -> None: ...
    def parse(self, contents: bytes) -> Tree: ...
