from __future__ import annotations

import re
from decimal import Decimal
from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.beans import create
from fava.core.filter_parser import _LEXER
from fava.core.filter_parser import CLOSE
from fava.core.filter_parser import CMP_OP
from fava.core.filter_parser import COMMA
from fava.core.filter_parser import DASH
from fava.core.filter_parser import EQ_OP
from fava.core.filter_parser import KEY
from fava.core.filter_parser import LINK
from fava.core.filter_parser import Match
from fava.core.filter_parser import MatchAmount
from fava.core.filter_parser import NUMBER
from fava.core.filter_parser import OPEN
from fava.core.filter_parser import parse_filter
from fava.core.filter_parser import STRING
from fava.core.filter_parser import TAG
from fava.util.parsing import ParseError
from fava.util.parsing import UnexpectedTokenError

if TYPE_CHECKING:  # pragma: no cover
    from fava.util.parsing import TokenKind


def lex(string: str) -> list[tuple[TokenKind[Any], Any]]:
    return [(t.kind, t.kind.value(t)) for t in _LEXER.tokenize(string)]


def test_match() -> None:
    assert Match("asdf")("asdf")
    assert Match("asdf")("asdfasdf")
    assert Match("asdf")("aasdfasdf")
    assert Match("^asdf")("asdfasdf")
    assert not Match("asdf")("fdsadfs")
    assert not Match("^asdf")("aasdfasdf")
    assert Match("(((")("(((")


def test_match_amount() -> None:
    one = Decimal(1)
    two = Decimal(2)

    one_amt = create.amount("1 EUR")
    two_amt = create.amount("2 EUR")
    three_amt = create.amount("3 EUR")

    assert MatchAmount("=", one)(one_amt)
    assert MatchAmount("=", one)(one_amt)

    assert MatchAmount(">", two)(three_amt)
    assert not MatchAmount(">", two)(two_amt)
    assert not MatchAmount(">", two)(one_amt)

    assert MatchAmount(">=", two)(three_amt)
    assert MatchAmount(">=", two)(two_amt)
    assert not MatchAmount(">=", two)(one_amt)

    assert not MatchAmount("<", two)(three_amt)
    assert not MatchAmount("<", two)(two_amt)
    assert MatchAmount("<", two)(one_amt)

    assert not MatchAmount("<=", two)(three_amt)
    assert MatchAmount("<=", two)(two_amt)
    assert MatchAmount("<=", two)(one_amt)


def test_lexer_basic() -> None:
    assert lex("#some_tag ^some_link -^some_link") == [
        (TAG, "some_tag"),
        (LINK, "some_link"),
        (DASH, "-"),
        (LINK, "some_link"),
    ]
    assert lex("'string' string \"string\"") == [
        (STRING, "string"),
        (STRING, "string"),
        (STRING, "string"),
    ]
    with pytest.raises(UnexpectedTokenError):
        lex('"')


def test_lexer_emoji() -> None:
    assert lex("☕ ⛽️") == [(STRING, "☕"), (STRING, "⛽️")]


def test_lexer_literals_in_string() -> None:
    assert lex("string-2-2 string") == [
        (STRING, "string-2-2"),
        (STRING, "string"),
    ]


def test_lexer_key() -> None:
    data = 'payee:asdfasdf ^some_link somekey:"testtest" units>80.2 '
    assert lex(data) == [
        (KEY, "payee"),
        (EQ_OP, ":"),
        (STRING, "asdfasdf"),
        (LINK, "some_link"),
        (KEY, "somekey"),
        (EQ_OP, ":"),
        (STRING, "testtest"),
        (KEY, "units"),
        (CMP_OP, ">"),
        (NUMBER, Decimal("80.2")),
    ]


def test_lexer_parentheses() -> None:
    data = "(payee:asdfasdf ^some_link) (somekey:'testtest')"
    assert lex(data) == [
        (OPEN, "("),
        (KEY, "payee"),
        (EQ_OP, ":"),
        (STRING, "asdfasdf"),
        (LINK, "some_link"),
        (CLOSE, ")"),
        (OPEN, "("),
        (KEY, "somekey"),
        (EQ_OP, ":"),
        (STRING, "testtest"),
        (CLOSE, ")"),
    ]


def test_lexer_comma() -> None:
    assert lex("#a,#b") == [(TAG, "a"), (COMMA, ","), (TAG, "b")]


@pytest.mark.parametrize(
    ("string", "error"),
    [
        ('who:"fff', """Unexpected '"' in parsed expression."""),
        ("#tag 'unterminated", "Unexpected ''' in parsed expression."),
        ("", "Unexpected 'end of input' in parsed expression."),
        ("-", "Unexpected 'end of input' in parsed expression."),
        ("(", "Unexpected 'end of input' in parsed expression."),
        ("any(", "Unexpected 'end of input' in parsed expression."),
        ("key:", "Unexpected 'end of input' in parsed expression."),
        (
            'any(who:"Martin"',
            "Unexpected 'end of input' in parsed expression.",
        ),
        ("#a #b)", "Unexpected ')' in parsed expression."),
        ("#a,", "Unexpected 'end of input' in parsed expression."),
        (",#a", "Unexpected ',' in parsed expression."),
        ("any(#a", "Unexpected 'end of input' in parsed expression."),
        ("(#a,#b", "Unexpected 'end of input' in parsed expression."),
        ("units>#a", "Unexpected '#a' in parsed expression."),
        ("payee:>", "Unexpected '>' in parsed expression."),
        ("payee)", "Unexpected ')' in parsed expression."),
    ],
)
def test_parse_filter_invalid(string: str, error: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error)):
        parse_filter(string)
