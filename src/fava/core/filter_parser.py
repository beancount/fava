"""Parsing of Fava's advanced filter syntax."""

from __future__ import annotations

import operator
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING

from fava.util.parsing import KeywordTokenKind
from fava.util.parsing import Lexer
from fava.util.parsing import LiteralTokenKind
from fava.util.parsing import ParserBase
from fava.util.parsing import TokenKind
from fava.util.parsing import UnexpectedTokenError

try:
    from typing import override
except ImportError:  # pragma: no cover
    from typing_extensions import override

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Iterable

    from fava.beans.abc import Directive
    from fava.beans.abc import Posting


def _unquote(text: str) -> str:
    """Strip the quotes from a string, if it is quoted."""
    return text[1:-1] if text[0] in {'"', "'"} else text


Operator = Literal["=", ">=", "<=", "<", ">"]


LINK = TokenKind(r"\^[A-Za-z0-9\-_/.]+", lambda s: s[1:])
TAG = TokenKind(r"\#[A-Za-z0-9\-_/.]+", lambda s: s[1:])
ALL = LiteralTokenKind("all(")
ANY = LiteralTokenKind("any(")
KEY = TokenKind(r"[a-z][a-zA-Z0-9\-_]+(?=\s*(?::|=|>=|<=|<|>))", str)
COLON = LiteralTokenKind(":")
CMP_OP: KeywordTokenKind[Operator] = KeywordTokenKind(Operator)
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
        COLON,
        CMP_OP,
        NUMBER,
        STRING,
        DASH,
        COMMA,
        OPEN,
        CLOSE,
    ),
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


_OPERATORS: dict[Operator, Callable[[Any, Decimal], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    ">": operator.gt,
    ">=": operator.ge,
}


class MatchAmount:
    """Matches an amount."""

    __slots__ = ("operator", "value")

    operator: Callable[[Any, Decimal], bool]
    value: Decimal

    def __init__(self, op: Operator, value: Decimal) -> None:
        self.value = value
        self.operator = _OPERATORS[op]

    def __call__(self, obj: Any) -> bool:
        """Whether the number of the given amount matches."""
        number = getattr(obj, "number", None)
        return (
            self.operator(abs(number), self.value)
            if number is not None
            else False
        )


class FilterExpression(ABC):
    """A part of a parsed filter, matching entries or postings."""

    @abstractmethod
    def __call__(self, entry: Directive | Posting) -> bool:
        """Whether the entry or posting matches this filter."""


@dataclass(frozen=True, slots=True)
class OrExpression(FilterExpression):
    """Match if any of the given expressions match."""

    expressions: tuple[FilterExpression, ...]

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return any(expr(entry) for expr in self.expressions)


@dataclass(frozen=True, slots=True)
class AndExpression(FilterExpression):
    """Match if all of the given expressions match."""

    expressions: tuple[FilterExpression, ...]

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return all(expr(entry) for expr in self.expressions)


@dataclass(frozen=True, slots=True)
class NotExpression(FilterExpression):
    """Match if the given expression does not match."""

    expression: FilterExpression

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return not self.expression(entry)


@dataclass(frozen=True, slots=True)
class TagMatch(FilterExpression):
    """Match entries that have the given tag."""

    tag: str

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        tags = getattr(entry, "tags", None)
        return (self.tag in tags) if tags is not None else False


@dataclass(frozen=True, slots=True)
class LinkMatch(FilterExpression):
    """Match entries that have the given link."""

    link: str

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        links = getattr(entry, "links", None)
        return (self.link in links) if links is not None else False


@dataclass(frozen=True, slots=True)
class StringMatch(FilterExpression):
    """Match entries by narration, payee or comment."""

    match: Match

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        for name in ("narration", "payee", "comment"):
            value = getattr(entry, name, "")
            if value and self.match(value):
                return True
        return False


@dataclass(frozen=True, slots=True)
class KeyMatch(FilterExpression):
    """Match entries by an attribute or metadata value of the given name."""

    key: str
    match: Match | MatchAmount

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        if hasattr(entry, self.key):
            return self.match(getattr(entry, self.key) or "")
        if entry.meta is not None and self.key in entry.meta:
            return self.match(entry.meta.get(self.key))
        return False


@dataclass(frozen=True, slots=True)
class UnitsMatch(FilterExpression):
    """Match entries that have a posting with matching units."""

    match: MatchAmount

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return any(
            self.match(posting.units)
            for posting in getattr(entry, "postings", [])
        )


@dataclass(frozen=True, slots=True)
class PostingUnitsMatch(FilterExpression):
    """Match a posting by its own units.

    This is the equivalent of :class:`UnitsMatch` for use directly inside an
    ``all(...)``/``any(...)`` expression, where an amount comparison should
    match the posting being considered itself rather than search its (in
    that context nonexistent) postings.
    """

    match: MatchAmount

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return self.match(getattr(entry, "units", None))


@dataclass(frozen=True, slots=True)
class PostingsMatch(FilterExpression):
    """Match entries by all or any of their postings matching."""

    quantifier: Callable[[Iterable[bool]], bool]
    expression: FilterExpression

    @override
    def __call__(self, entry: Directive | Posting) -> bool:
        return self.quantifier(
            self.expression(posting)
            for posting in getattr(entry, "postings", [])
        )


class _FilterParser(ParserBase):
    """A parser for Fava's advanced filter syntax.

    The grammar is the following, where inside an 'all(...)' or 'any(...)'
    expression, ALL, ANY, TAG, LINK and STRING are not allowed and CMP_OP
    NUMBER matches the posting under consideration itself rather than
    searching the (in that context nonexistent) postings of an entry::

        filter   := or_expr
        or_expr  := and_expr {',' and_expr}
        and_expr := unary {unary}
        unary    := '-' unary | atom
        atom     := '(' or_expr ')'
                  | ALL or_expr ')' | ANY or_expr ')'
                  | TAG | LINK | STRING
                  | KEY COLON STRING | KEY CMP_OP NUMBER
                  | CMP_OP NUMBER
    """

    def __init__(self, string: str) -> None:
        super().__init__(list(_LEXER.tokenize(string)))

    def parse(self) -> FilterExpression:
        """Parse the whole filter into a matching expression."""
        expr = self._or_expression(in_postings=False)
        if remaining := self.peek():
            raise UnexpectedTokenError(remaining.text)
        return expr

    def _or_expression(self, *, in_postings: bool) -> FilterExpression:
        """Parse expressions separated by commas - matching any of them."""
        expressions = [self._and_expression(in_postings=in_postings)]
        while self.accept(COMMA):
            expressions.append(self._and_expression(in_postings=in_postings))
        if len(expressions) == 1:
            return expressions[0]
        return OrExpression(tuple(expressions))

    def _and_expression(self, *, in_postings: bool) -> FilterExpression:
        """Parse expressions separated by spaces - matching all of them."""
        expressions = [self._unary_expression(in_postings=in_postings)]
        while self.peek_kind() in (
            ALL,
            ANY,
            CMP_OP,
            DASH,
            KEY,
            LINK,
            OPEN,
            STRING,
            TAG,
        ):
            expressions.append(self._unary_expression(in_postings=in_postings))
        if len(expressions) == 1:
            return expressions[0]
        return AndExpression(tuple(expressions))

    def _unary_expression(self, *, in_postings: bool) -> FilterExpression:
        """Parse an expression, which might be negated."""
        if self.accept(DASH):
            expr = self._unary_expression(in_postings=in_postings)
            return NotExpression(expr)
        return self._atom(in_postings=in_postings)

    def _atom(self, *, in_postings: bool) -> FilterExpression:  # noqa: PLR0911
        """Parse a parenthesised or simple expression.

        Some kinds of expression only make sense when matching an entry and
        are not allowed inside an 'all(...)'/'any(...)' expression, which
        matches postings instead - `in_postings` tracks this context.
        """
        token = self.advance()
        kind = token.kind
        if kind is OPEN:
            expr = self._or_expression(in_postings=in_postings)
            self.expect(CLOSE)
            return expr
        if kind is ALL and not in_postings:
            return self._quantified(all)
        if kind is ANY and not in_postings:
            return self._quantified(any)
        if kind is TAG and not in_postings:
            return TagMatch(TAG.value(token))
        if kind is LINK and not in_postings:
            return LinkMatch(LINK.value(token))
        if kind is STRING and not in_postings:
            return StringMatch(Match(STRING.value(token)))
        if kind is KEY:
            return self._key(KEY.value(token))
        if kind is CMP_OP:
            match = MatchAmount(CMP_OP.value(token), self.expect(NUMBER))
            if in_postings:
                return PostingUnitsMatch(match)
            return UnitsMatch(match)
        raise UnexpectedTokenError(token.text)

    def _quantified(
        self,
        quantifier: Callable[[Iterable[bool]], bool],
    ) -> FilterExpression:
        """Parse the rest of an 'all(...)' or 'any(...)' expression."""
        expr = self._or_expression(in_postings=True)
        self.expect(CLOSE)
        return PostingsMatch(quantifier, expr)

    def _key(self, key: str) -> FilterExpression:
        """Parse the rest of an expression matching an attribute value."""
        # A KEY only matches if one of the operators follows it.
        if self.accept(COLON):
            return KeyMatch(key, Match(self.expect(STRING)))
        op = self.expect(CMP_OP)
        return KeyMatch(key, MatchAmount(op, self.expect(NUMBER)))


def parse_filter(string: str) -> FilterExpression:
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
    - 'any(...)' and 'all(...)', matching entries by their postings - tags,
      links, strings and nested 'any(...)'/'all(...)' are not allowed inside
      them, and '>= 100' there matches the posting's own units directly

    Args:
        string: The filter string.

    Returns:
        A FilterExpression matching entries against the filter.

    Raises:
        FilterError: If the filter could not be parsed.
    """
    return _FilterParser(string).parse()
