# pylint: disable=missing-docstring

import textwrap

import pytest

from fava.parser.parser import parse_string


@pytest.fixture
def parse_doc(request):
    string = request.function.__doc__
    string_ = textwrap.dedent(string)
    return parse_string(string_)


@pytest.fixture
def snapshot_parse_doc(request, snapshot):
    string = request.function.__doc__
    string_ = textwrap.dedent(string)
    entries, errors, options = parse_string(string_)
    snapshot((entries, errors))
    return entries, errors, options
