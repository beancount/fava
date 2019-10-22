"""Beancount parser using tree-sitter.

This uses a tree-sitter grammar to provide an alternative parser to the one
shipped with Beancount, which is a flex/yacc parser.
"""
import copy
from collections import defaultdict
from importlib.machinery import EXTENSION_SUFFIXES
from typing import Any
from typing import DefaultDict
from typing import List
from typing import Optional
from typing import Set

from beancount.core.data import ALL_DIRECTIVES
from beancount.core.display_context import DisplayContext
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.parser import options
from beancount.parser.grammar import ParserError
from pkg_resources import resource_filename
from tree_sitter import Language
from tree_sitter import Parser

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
        self.errors: List[ParserError] = []
        #: Beancount options
        self.options = copy.deepcopy(options.OPTIONS_DEFAULTS)
        self.options["filename"] = filename
        #: The name of the file that is currently being parsed.
        self.filename: Optional[str] = filename
        #: The file contents in bytes
        self.contents: bytes = contents
        dcontext = DisplayContext()
        self._dcupdate = dcontext.update
        self.options["dcontext"] = dcontext

    def finalize(self):
        """Check for unbalanced tags and metadata."""
        for tag in self.tags:
            self.error(None, "Unbalanced pushed tag: '{}'".format(tag))

        for key, value_list in self.meta.items():
            self.error(
                None,
                "Unbalanced metadata key '{}'; leftover metadata '{}'".format(
                    key, str(value_list)
                ),
            )

    def dcupdate(self, number, currency):
        """Update the display context."""
        if (
            isinstance(number, Decimal)
            and currency
            and currency is not MISSING
        ):
            self._dcupdate(number, currency)

    def error(self, node, msg: str) -> None:
        """Add a parser error.

        Args:
            node: The syntax node (to get the positions)
            msg: The error message.
        """
        meta = self.metadata(node)
        self.errors.append(ParserError(meta, msg, None))

    def handle_option(self, node, name: str, value: str) -> None:
        """Set an option."""

        if name not in self.options:
            return self.error(node, "Invalid option: '{}'".format(name))
        if name in options.READ_ONLY_OPTIONS:
            return self.error(node, "Options '{}' may not be set".format(name))
        option_descriptor = options.OPTIONS[name]

        # Issue error for deprecated options.
        if option_descriptor.deprecated:
            self.error(node, option_descriptor.deprecated)
        # Rename option if it is an alias.
        if option_descriptor.alias:
            name = option_descriptor.alias
            option_descriptor = options.OPTIONS[name]
        if option_descriptor.converter:
            try:
                value = option_descriptor.converter(value)
            except ValueError as exc:
                return self.error(
                    node, "Error for option '{}': {}".format(name, exc)
                )
        option = self.options[name]

        if isinstance(option, list):
            option.append(value)

        elif isinstance(option, dict):
            try:
                dict_key, dict_value = value
            except ValueError as exc:
                return self.error(
                    node, "Error for option '{}': {}".format(name, exc)
                )
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

    def metadata(self, node):
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

    def handle_node(self, node):
        """Obtain the parsed value of a node in the syntax tree.

        For named nodes in the grammar, try to handle them using a function
        from `.handlers`."""
        type_ = node.type
        if node.is_named:
            handler = getattr(handlers, type_)
            return handler(self, node)
        return node

    def get(self, node, field):
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


def parse_bytes(contents: bytes, filename: str = None):
    """Parse the given bytes.

    Args:
        contents: The bytes to parse.
        filename: Optional filename.
    """

    tree = PARSER.parse(contents)
    root = tree.root_node
    state = ParserState(contents, filename)

    entries = []
    for entry in root.children:
        res = state.handle_node(entry)
        if isinstance(res, ALL_DIRECTIVES):
            entries.append(res)
        else:
            pass

    state.finalize()
    return entries, state.errors, state.options


def parse_string(contents: str, filename: str = None):
    """Parse the given string.

    Args:
        contents: The string to parse.
        filename: Optional filename.
    """

    return parse_bytes(contents.encode(), filename)


def parse_file(filename: str, **_):
    """Parse a file.

    Args:
        filename: Path to the file.
    """
    with open(filename, "rb") as file_descriptor:
        contents = file_descriptor.read()

    return parse_bytes(contents, filename)
