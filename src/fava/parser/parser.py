"""Beancount parser using tree-sitter.

This uses a tree-sitter grammar to provide an alternative parser to the one
shipped with Beancount, which is a flex/yacc parser.
"""
import logging
from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from beancount.core.data import Entries
from beancount.core.number import MISSING
from pkg_resources import resource_filename
from tree_sitter import Language
from tree_sitter import Node
from tree_sitter import Parser

from fava.helpers import BeancountError
from fava.parser import nodes as handlers
from fava.parser.state import BaseState
from fava.util import log_time

LOG = logging.getLogger(__name__)


class ParserState(BaseState):
    """The state of the parser.

    This is where data that needs to be kept in the state lives.
    """

    def finalize(self) -> None:
        """Check for unbalanced tags and metadata."""
        for tag in self.tags:
            self.error(None, f"Unbalanced pushed tag: '{tag}'")

        for key, value_list in self.meta.items():
            self.error(
                None,
                f"Unbalanced metadata key '{key}'; "
                f"leftover metadata '{str(value_list)}'",
            )

    def dcupdate(self, number, currency) -> None:
        """Update the display context.

        One or both of the arguments might be `MISSING`, in which case we do
        nothing.

        Args:
            number: The number.
            currency: The currency.
        """
        if number is not MISSING and currency is not MISSING:
            self._dcupdate(number, currency)

    def handle_node(self, node: Node):
        """Obtain the parsed value of a node in the syntax tree.

        For named nodes in the grammar, try to handle them using a function
        from `.handlers`."""
        type_ = node.type
        if node.is_named:
            handler = getattr(handlers, type_)
            return handler(self, node)
        return node

    def get(self, node: Node, field: str) -> Optional[Any]:
        """Get the named node field."""
        child = node.child_by_field_name(field)
        if child is None:
            return None
        return self.handle_node(child)


EXT = EXTENSION_SUFFIXES[-1]
BEANCOUNT_LANGUAGE = Language(
    resource_filename("fava.parser", "tree_sitter_beancount" + EXT),
    "beancount",
)

PARSER = Parser()
PARSER.set_language(BEANCOUNT_LANGUAGE)


ParserResult = Tuple[Entries, List[BeancountError], Any]


def _recursive_parse(
    nodes: List[Node],
    state: ParserState,
    filename: Optional[str],
    seen_files: Set[str],
) -> Entries:
    """Parse the given file recursively.

    When an include directive is found, we recurse down. So the files are
    traversed in the order of a depth-first-search.

    Args:
        nodes: A list of top-level syntax tree nodes.
        state: The current ParserState (with .contents and .filename set for
            this file).
        filename: The absolute path to the file (if it is None, we do not
            recurse).
        seen_files: The set of already parsed files.
    """
    entries: Entries = []
    for node in nodes:
        try:
            res = state.handle_node(node)
            if res is not None:
                entries.append(res)
        except handlers.SyntaxError:
            node_contents = state.contents[
                node.start_byte : node.end_byte
            ].decode()
            state.error(
                node,
                "Syntax error with transaction:\n"
                f"{node_contents}\n{node.sexp()}",
            )
        except handlers.IncludeFound as incl:
            if filename is None:
                state.error(
                    node, "Cannot resolve include when parsing a string."
                )
                continue

            included_expanded = sorted(
                Path(filename).parent.glob(incl.filename)
            )
            if not included_expanded:
                state.error(node, "Include glob did not match any files.")
                continue

            for included in included_expanded:
                included_name = str(included.resolve())
                if included_name in seen_files:
                    state.error(node, f"Duplicate included file: {filename}")
                    continue
                contents = included.read_bytes()
                seen_files.add(included_name)
                with log_time(f"parsing {included_name}", LOG):
                    tree = PARSER.parse(contents)
                # Update state for the included file and recurse.
                with state.set_current_file(contents, included_name):
                    included_entries = _recursive_parse(
                        tree.root_node.children,
                        state,
                        included_name,
                        seen_files,
                    )
                    entries.extend(included_entries)
    return entries


def parse_bytes(contents: bytes, filename: str = None) -> ParserResult:
    """Parse the given bytes.

    Args:
        contents: The bytes to parse.
        filename: Optional filename.
    """
    # The parser state.
    state = ParserState(contents, filename)

    # A set of the loaded files to avoid include cycles. This should only
    # contain absolute and resolved paths.
    seen_files: Set[str] = set()

    if filename:
        filename = str(Path(filename).resolve())
        seen_files.add(filename)

    with log_time(f"parsing {filename}", LOG):
        tree = PARSER.parse(contents)
    entries = _recursive_parse(
        tree.root_node.children, state, filename, seen_files
    )

    state.finalize()
    state.options["include"] = sorted(seen_files)
    return entries, state.errors, state.options


def parse_string(contents: str, filename: str = None) -> ParserResult:
    """Parse the given string.

    Args:
        contents: The string to parse.
        filename: Optional filename.
    """

    return parse_bytes(contents.encode(), filename)


def parse_file(filename: str) -> ParserResult:
    """Parse a file.

    Args:
        filename: Path to the file.
    """
    contents = Path(filename).read_bytes()
    return parse_bytes(contents, filename)
