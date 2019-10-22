"""Loader for Beancount files."""

from unittest import mock

from beancount import loader
from beancount.parser import parser

from fava.parser.parser import parse_file


def load_file(filename, tree_sitter=True):
    """Load a file, using either Beancount's parser or the tree-sitter one."""
    # pylint: disable=protected-access
    replace = parse_file if tree_sitter else parser.parse_file
    with mock.patch("beancount.parser.parser.parse_file", new=replace):
        return loader._load([(filename, True)], None, None, None)
