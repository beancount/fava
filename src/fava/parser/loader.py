"""Loader for Beancount files."""
import logging

from beancount.core.data import entry_sortkey
from beancount.loader import _load
from beancount.loader import compute_input_hash
from beancount.loader import load_file as beancount_load_file
from beancount.loader import run_transformations
from beancount.ops import validation  # type: ignore
from beancount.parser import booking  # type: ignore

from fava.helpers import BeancountError
from fava.parser.parser import parse_file
from fava.util import log_time

LOG = logging.getLogger(__name__)


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


def load_file(filename: str, tree_sitter=True, is_encrypted=False):
    """Load a file, using either Beancount's parser or the tree-sitter one.

    Args:
        filename: The file to load.
        tree_sitter: Whether to use the tree-sitter based parser.
        is_encrypted: Whether the file is encrypted.
    """
    if is_encrypted:
        return beancount_load_file(filename)
    with log_time("Beancount parser", LOG):
        ret_bc = _load([(filename, True)], None, None, None)
    if tree_sitter is False:
        return ret_bc
    with log_time("tree-sitter parser", LOG):
        ret_fava = _load_tree_sitter(filename)
    for left, right in zip(ret_bc[0], ret_fava[0]):
        if left != right:
            msg = f"Mismatch:\n{left}\n\n{right}"
            print(msg)
            ret_fava[1].append(BeancountError(None, msg, right))
    return ret_fava
