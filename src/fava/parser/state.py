"""
The parser state.
"""
import copy
from collections import defaultdict
from contextlib import contextmanager
from typing import Any
from typing import Callable
from typing import DefaultDict
from typing import List
from typing import Optional
from typing import Set

from beancount.core.display_context import DisplayContext
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.parser.grammar import ParserError
from beancount.parser.options import OPTIONS  # type: ignore
from beancount.parser.options import OPTIONS_DEFAULTS  # type: ignore
from beancount.parser.options import READ_ONLY_OPTIONS  # type: ignore
from tree_sitter import Node

from fava.helpers import BeancountError


class BaseState:
    """The state of the parser.

    This is where data that needs to be kept in the state lives.
    """

    __slots__ = (
        "_dcupdate",
        "contents",
        "errors",
        "filename",
        "meta",
        "options",
        "tags",
    )

    def __init__(self, contents: bytes, filename: str = None):
        #: The current stack of tags.
        self.tags: Set[str] = set()
        #: The currently pushed metadata items.
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
        orig_meta = copy.deepcopy(self.meta)
        self.contents = contents
        self.filename = filename
        try:
            yield
        finally:
            if orig_meta != self.meta:
                self.error(None, "Unbalanced metadata")
            self.meta = orig_meta
            self.contents = orig_contents
            self.filename = orig_filename

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

    def metadata(self, node: Optional[Node], offset=0):
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
        meta["lineno"] = node.start_point[0] + 1 + offset

        return meta

    def handle_node(self, node: Node):
        """Obtain the parsed value of a node in the syntax tree.

        For named nodes in the grammar, try to handle them using a function
        from `.handlers`."""
        raise NotImplementedError

    def get(self, node: Node, field: str) -> Any:
        """Get the named node field."""
        raise NotImplementedError
