"""Beancount parser using tree-sitter.

This uses a tree-sitter grammar to provide an alternative parser to the one
shipped with Beancount, which is a flex/yacc parser.
"""
import copy
from collections import defaultdict
from contextlib import contextmanager
from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path
from typing import Any
from typing import Callable
from typing import DefaultDict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from beancount.core.data import ALL_DIRECTIVES
from beancount.core.data import Entries
from beancount.core.display_context import DisplayContext
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.parser.grammar import ParserError
from beancount.parser.options import OPTIONS  # type: ignore
from beancount.parser.options import OPTIONS_DEFAULTS  # type: ignore
from beancount.parser.options import READ_ONLY_OPTIONS  # type: ignore
from pkg_resources import resource_filename
from tree_sitter import Language
from tree_sitter import Node
from tree_sitter import Parser

from fava.core.helpers import BeancountError
from fava.parser import nodes as handlers


class ParserState:
    """The state of the parser.

    This is where data that needs to be kept in the state lives.
    """

    def __init__(self, contents: bytes, filename: str = None):
        #: The current stack of tags.
        self.tags: Set[str] = set()
        #: The current stacks of tags.
        self.meta: DefaultDict[str, Any] = defaultdict(list)
        #: List or errors.
        self.errors: List[BeancountError] = []
        #: Beancount options
        self.options = copy.deepcopy(OPTIONS_DEFAULTS)
        self.options["filename"] = filename
        #: The name of the file that is currently being parsed.
        self.filename: Optional[str] = filename
        #: The file contents in bytes
        self.contents: bytes = contents
        dcontext = DisplayContext()
        self._dcupdate: Callable[[Decimal, str], None] = dcontext.update
        self.options["dcontext"] = dcontext

    @contextmanager
    def set_current_file(self, contents: bytes, filename: str):
        """Context manager to set the current file.

        When parsing included files recursively, we need to update the current
        file in the state while we handle the included file and the reset it
        back when we continue with the including file.

        Args:
            contents: The contents of the included file in bytes.
            filename: The filename of the included file.
        """
        orig_contents = self.contents
        orig_filename = self.filename
        self.contents = contents
        self.filename = filename
        try:
            yield
        finally:
            self.contents = orig_contents
            self.filename = orig_filename

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

    def error(self, node: Optional[Node], msg: str) -> None:
        """Add a parser error.

        Args:
            node: The syntax node (to get the positions)
            msg: The error message.
        """
        meta = self.metadata(node)
        self.errors.append(ParserError(meta, msg, None))

    def handle_option(self, node: Node, name: str, value: Any) -> None:
        """Set an option."""

        if name not in self.options:
            return self.error(node, f"Invalid option: '{name}'")
        if name in READ_ONLY_OPTIONS:
            return self.error(
                node, f"Option '{name}' is read-only and may not be set",
            )
        option_descriptor = OPTIONS[name]

        # Issue error for deprecated options.
        if option_descriptor.deprecated:
            self.error(node, option_descriptor.deprecated)
        # Rename option if it is an alias.
        if option_descriptor.alias:
            name = option_descriptor.alias
            option_descriptor = OPTIONS[name]
        if option_descriptor.converter:
            try:
                value = option_descriptor.converter(value)
            except ValueError as exc:
                return self.error(node, f"Error for option '{name}': {exc}")
        option = self.options[name]

        if isinstance(option, list):
            option.append(value)

        elif isinstance(option, dict):
            try:
                dict_key, dict_value = value
            except ValueError as exc:
                return self.error(node, f"Error for option '{name}': {exc}")
            option[dict_key] = dict_value

        elif isinstance(option, bool):
            # Convert to a boolean.
            if not isinstance(value, bool):
                value = (value.lower() in {"true", "on"}) or (value == "1")
            self.options[name] = value

        else:
            # Set the value.
            self.options[name] = value

        return None

    def metadata(self, node: Optional[Node]):
        """Metadata with the position for a node.

        Args:
            node: The node in the syntax tree that this metadata is for.
        """
        if node is None:
            return {"filename": self.filename, "lineno": 0}
        meta = {}
        if self.meta:
            for key, value_list in self.meta.items():
                meta[key] = value_list[-1]
        node_meta = self.get(node, "metadata")
        if node_meta:
            meta.update(node_meta)
        meta["filename"] = self.filename
        meta["lineno"] = node.start_point[0] + 1

        return meta

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
            if isinstance(res, ALL_DIRECTIVES):
                entries.append(res)
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
