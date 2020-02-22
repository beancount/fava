"""Loader for Beancount files."""
from beancount.loader import compute_input_hash
from beancount.loader import run_transformations
from beancount.loader import _load
from beancount.core.data import entry_sortkey
from beancount.parser import booking  # type: ignore
from beancount.ops import validation  # type: ignore

from fava.parser.parser import parse_file


def _load_tree_sitter(filename: str):
    entries, parse_errors, options_map = parse_file(filename)
    entries.sort(key=entry_sortkey)

    entries, balance_errors = booking.book(entries, options_map)
    parse_errors.extend(balance_errors)

    entries, errors = run_transformations(
        entries, parse_errors, options_map, None
    )

    valid_errors = validation.validate(entries, options_map, None, None)
    errors.extend(valid_errors)

    options_map["input_hash"] = compute_input_hash(options_map["include"])

    return entries, errors, options_map


def load_file(filename: str, tree_sitter=True):
    """Load a file, using either Beancount's parser or the tree-sitter one."""
    # pylint: disable=protected-access
    if tree_sitter is False:
        return _load([(filename, True)], None, None, None)
    return _load_tree_sitter(filename)
