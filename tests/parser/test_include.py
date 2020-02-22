# pylint: disable=missing-docstring
from pathlib import Path

from fava.parser.parser import parse_file


def test_include_in_string(parse_doc):
    """
    include "test"
    """
    _, errors, options_map = parse_doc
    assert options_map["include"] == []
    assert len(errors) == 1


def test_include():
    entries, errors, options_map = parse_file(
        str(Path(__file__).parent / "data" / "include.beancount")
    )
    assert len(entries) == 3
    assert not errors
    dcontext = options_map["dcontext"]
    # Display context get's updated in included files
    assert "USD" in dcontext.ccontexts
    assert len(options_map["include"]) == 3
