"""Parsing of Fava's advanced filter syntax."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any
from typing import TYPE_CHECKING

from fava.helpers import FavaAPIError
from fava.util.parsing import Lexer
from fava.util.parsing import LiteralTokenKind
from fava.util.parsing import ParseError
from fava.util.parsing import ParserBase
from fava.util.parsing import TokenKind
from fava.util.parsing import UnexpectedTokenError

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Iterable

    from fava.beans.abc import Directive

    #: A filter, matching entries or postings.
    FilterFunction = Callable[[Any], bool]


class FilterError(FavaAPIError):
    """Filter exception."""


def _unquote(text: str) -> str:
    """Strip the quotes from a string, if it is quoted."""
    return text[1:-1] if text[0] in {'"', "'"} else text


LINK = TokenKind(r"\^[A-Za-z0-9\-_/.]+", lambda s: s[1:])
TAG = TokenKind(r"\#[A-Za-z0-9\-_/.]+", lambda s: s[1:])
ALL = LiteralTokenKind("all(")
ANY = LiteralTokenKind("any(")
KEY = TokenKind(r"[a-z][a-zA-Z0-9\-_]+(?=\s*(?::|=|>=|<=|<|>))", str)
EQ_OP = LiteralTokenKind(":")
CMP_OP = TokenKind(r"=|>=|<=|<|>", str)
NUMBER = TokenKind(r"\d*\.?\d+", Decimal)
STRING = TokenKind(r"""\w[-\w]*|"[^"]*"|'[^']*'|[^\s\-(),#^:="']+""", _unquote)
DASH = LiteralTokenKind("-")
COMMA = LiteralTokenKind(",")
OPEN = LiteralTokenKind("(")
CLOSE = LiteralTokenKind(")")

#: The lexer for filters. The kinds for the single characters '-,()' need to
#: come last, since a string can contain them - the patterns before them match
#: those cases and only leave the ones where they stand on their own.
_LEXER = Lexer(
    (
        LINK,
        TAG,
        ALL,
        ANY,
        KEY,
        EQ_OP,
        CMP_OP,
        NUMBER,
        STRING,
        DASH,
        COMMA,
        OPEN,
        CLOSE,
    ),
)

#: The kinds of token that an expression can start with.
_EXPRESSION_START: frozenset[TokenKind[Any]] = frozenset(
    {ALL, ANY, CMP_OP, DASH, KEY, LINK, OPEN, STRING, TAG}
)


class Match:
    """Match a string."""

    __slots__ = ("match",)

    match: Callable[[str], bool]

    def __init__(self, search: str) -> None:
        try:
            match = re.compile(search, re.IGNORECASE).search
            self.match = lambda s: bool(match(s))
        except re.error:
            self.match = lambda s: s == search

    def __call__(self, obj: Any) -> bool:
        """Whether the string representation of the object matches."""
        return self.match(str(obj))


class MatchAmount:
    """Matches an amount."""

    __slots__ = ("match",)

    match: Callable[[Decimal], bool]

    def __init__(self, op: str, value: Decimal) -> None:
        if op == "=":
            self.match = lambda x: x == value
        elif op == ">=":
            self.match = lambda x: x >= value
        elif op == "<=":
            self.match = lambda x: x <= value
        elif op == ">":
            self.match = lambda x: x > value
        else:  # op == "<":
            self.match = lambda x: x < value

    def __call__(self, obj: Any) -> bool:
        """Whether the number of the given amount matches."""
        # Compare to the absolute value to simplify this filter.
        number = getattr(obj, "number", None)
        return self.match(abs(number)) if number is not None else False


def _match_tag(tag: str) -> FilterFunction:
    """Match entries that have the given tag."""

    def _tag(entry: Directive) -> bool:
        tags = getattr(entry, "tags", None)
        return (tag in tags) if tags is not None else False

    return _tag


def _match_link(link: str) -> FilterFunction:
    """Match entries that have the given link."""

    def _link(entry: Directive) -> bool:
        links = getattr(entry, "links", None)
        return (link in links) if links is not None else False

    return _link


def _match_string(string: str) -> FilterFunction:
    """Match entries by narration, payee or comment."""
    match = Match(string)

    def _string(entry: Directive) -> bool:
        for name in ("narration", "payee", "comment"):
            value = getattr(entry, name, "")
            if value and match(value):
                return True
        return False

    return _string


def _match_key(key: str, match: Match | MatchAmount) -> FilterFunction:
    """Match entries by an attribute or metadata value of the given name."""

    def _key(entry: Directive) -> bool:
        if hasattr(entry, key):
            return match(getattr(entry, key) or "")
        if entry.meta is not None and key in entry.meta:
            return match(entry.meta.get(key))
        return False

    return _key


def _match_units(match: MatchAmount) -> FilterFunction:
    """Match entries that have a posting with matching units."""

    def _units(entry: Directive) -> bool:
        return any(
            match(posting.units) for posting in getattr(entry, "postings", [])
        )

    return _units


def _match_postings(
    quantifier: Callable[[Iterable[bool]], bool],
    expr: FilterFunction,
) -> FilterFunction:
    """Match entries by all or any of their postings matching."""

    def _postings(entry: Directive) -> bool:
        return quantifier(
            expr(posting) for posting in getattr(entry, "postings", [])
        )

    return _postings


class _FilterParser(ParserBase):
    """A parser for Fava's advanced filter syntax.

    The grammar is the following::

        filter   := or_expr
        or_expr  := and_expr {',' and_expr}
        and_expr := unary {unary}
        unary    := '-' unary | atom
        atom     := '(' or_expr ')'
                  | ALL or_expr ')' | ANY or_expr ')'
                  | TAG | LINK | STRING
                  | KEY EQ_OP STRING | KEY CMP_OP NUMBER
                  | CMP_OP NUMBER
    """

    def __init__(self, string: str) -> None:
        super().__init__(list(_LEXER.tokenize(string)))

    def parse(self) -> FilterFunction:
        """Parse the whole filter into a matching function."""
        expr = self._or_expression()
        if remaining := self.peek():
            raise UnexpectedTokenError(remaining.text)
        return expr

    def _or_expression(self) -> FilterFunction:
        """Parse expressions separated by commas - matching any of them."""
        expressions = [self._and_expression()]
        while self.accept(COMMA):
            expressions.append(self._and_expression())
        if len(expressions) == 1:
            return expressions[0]
        return lambda entry: any(expr(entry) for expr in expressions)

    def _and_expression(self) -> FilterFunction:
        """Parse expressions separated by spaces - matching all of them."""
        expressions = [self._unary_expression()]
        while self.peek_kind() in _EXPRESSION_START:
            expressions.append(self._unary_expression())
        if len(expressions) == 1:
            return expressions[0]
        return lambda entry: all(expr(entry) for expr in expressions)

    def _unary_expression(self) -> FilterFunction:
        """Parse an expression, which might be negated."""
        if self.accept(DASH):
            expr = self._unary_expression()
            return lambda entry: not expr(entry)
        return self._atom()

    def _atom(self) -> FilterFunction:  # noqa: PLR0911
        """Parse a parenthesised or simple expression."""
        token = self.advance()
        kind = token.kind
        if kind is OPEN:
            expr = self._or_expression()
            self.expect(CLOSE)
            return expr
        if kind is ALL:
            return self._quantified(all)
        if kind is ANY:
            return self._quantified(any)
        if kind is TAG:
            return _match_tag(TAG.value(token))
        if kind is LINK:
            return _match_link(LINK.value(token))
        if kind is STRING:
            return _match_string(STRING.value(token))
        if kind is KEY:
            return self._key(KEY.value(token))
        if kind is CMP_OP:
            op = CMP_OP.value(token)
            return _match_units(MatchAmount(op, self.expect(NUMBER)))
        raise UnexpectedTokenError(token.text)

    def _quantified(
        self,
        quantifier: Callable[[Iterable[bool]], bool],
    ) -> FilterFunction:
        """Parse the rest of an 'all(...)' or 'any(...)' expression."""
        expr = self._or_expression()
        self.expect(CLOSE)
        return _match_postings(quantifier, expr)

    def _key(self, key: str) -> FilterFunction:
        """Parse the rest of an expression matching an attribute value."""
        # A KEY only matches if one of the operators follows it.
        if self.accept(EQ_OP):
            return _match_key(key, Match(self.expect(STRING)))
        op = self.expect(CMP_OP)
        return _match_key(key, MatchAmount(op, self.expect(NUMBER)))


def parse_filter(string: str) -> FilterFunction:
    """Parse a filter expression.

    Filters can be combined by separating them with spaces to match entries
    satisfying all of them or with commas to match entries satisfying at
    least one of them. A filter can be negated by prepending a '-' and
    filters can be grouped with parentheses. The simple filters are:

    - '#tag' and '^link'
    - a string, matching narration, payee or comment
    - 'key:"value"' and 'key >= 100', matching an entry attribute or
      metadata value
    - '>= 100', matching entries with a posting with those units
    - 'any(...)' and 'all(...)', matching entries by their postings

    Args:
        string: The filter string.

    Returns:
        A function matching entries against the filter.

    Raises:
        FilterError: If the filter could not be parsed.
    """
    try:
        return _FilterParser(string).parse()
    except ParseError as error:
        message = f"Failed to parse filter, {error}"
        raise FilterError(message) from error
