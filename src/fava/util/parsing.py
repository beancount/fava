"""Lexing and parsing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import Generic
from typing import get_args
from typing import Literal
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Iterator
    from collections.abc import Sequence

T = TypeVar("T")


class ParseError(ValueError):
    """An expression could not be parsed."""


class UnexpectedTokenError(ParseError):
    """An expression contained something that does not belong there."""

    def __init__(self, unexpected: str) -> None:
        super().__init__(f"Unexpected '{unexpected}' in parsed expression.")


class UnexpectedEndError(UnexpectedTokenError):
    """An expression ended before it was complete."""

    def __init__(self) -> None:
        super().__init__("end of input")


@dataclass(frozen=True, eq=False)
class TokenKind(Generic[T]):
    """A token type: pattern and how to get the value of such a token."""

    pattern: str
    convert: Callable[[str], T]

    def value(self, token: Token) -> T:
        """The value of a token, which has to be of this kind."""
        return self.convert(token.text)


class LiteralTokenKind(TokenKind[str]):
    """A token for a literal character or string."""

    def __init__(self, char: str) -> None:
        super().__init__(re.escape(char), str)


class KeywordTokenKind(TokenKind[T]):
    """A token for one of the keywords of a :class:`typing.Literal`."""

    def __init__(self, keywords: Any) -> None:
        # Match the longest keyword first
        _keywords: list[str] = sorted(get_args(keywords), key=len)[::-1]
        assert all(kw == kw.lower() for kw in _keywords)  # noqa: S101
        super().__init__(
            "|".join(re.escape(kw) for kw in _keywords),
            cast(
                "Callable[[str], T]",
                lambda s: s.lower(),
            ),
        )


@dataclass(frozen=True)
class Token:
    """A token, of some kind and with the text that it matched."""

    #: The kind of token that matched.
    kind: TokenKind[Any]
    #: The matched text.
    text: str


class Lexer:
    """Splits strings into tokens of the given kinds.

    They are matched in the order in which they are given. Text matching the
    skip pattern is ignored and any other character that does not start a token
    is an error.

    Args:
        rules: The kinds of token to split the string into.
        error: The exception to raise for a character that cannot start a
            token - it is passed that character.
        flags: re flags to apply.
        skip: A pattern for the text between tokens, which is ignored.
    """

    def __init__(
        self,
        rules: Sequence[TokenKind[Any]],
        /,
        *,
        error: Callable[[str], Exception] = UnexpectedTokenError,
        flags: int = 0,
        skip: str = r"\s+",
    ) -> None:
        self._rules = tuple(rules)
        self._error = error
        # Each kind is matched by a group named after its index - prefixed,
        # since group names need to be identifiers. The two groups at the end
        # match everything that is not a token, so that no character is
        # passed over silently.
        self._regex = re.compile(
            "|".join(
                f"(?P<RULE{index}>{kind.pattern})"
                for index, kind in enumerate(self._rules)
            )
            + rf"|(?P<SKIP>{skip})|(?P<ERROR>.)",
            flags,
        )

    def tokenize(self, string: str) -> Iterator[Token]:
        """Split a string into tokens.

        Yields:
            The tokens of the given string.

        Raises:
            Exception: The error for a character that cannot start a token.
        """
        for match in self._regex.finditer(string):
            name = match.lastgroup or "ERROR"
            if name == "SKIP":
                continue
            if name == "ERROR":
                raise self._error(match.group())
            index = int(name.removeprefix("RULE"))
            yield Token(self._rules[index], match.group())


class ParserBase:
    """A parser base class."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        self._tokens = tokens
        self._pos = 0
        self._len = len(self._tokens)

    def peek(self, offset: Literal[0, 1] = 0) -> Token | None:
        """The token at the given offset from the current position."""
        pos = self._pos + offset
        return self._tokens[pos] if pos < self._len else None

    def peek_kind(self, offset: Literal[0, 1] = 0) -> TokenKind[Any] | None:
        """The token kind at the given offset from the current position."""
        pos = self._pos + offset
        return self._tokens[pos].kind if pos < self._len else None

    def advance(self) -> Token:
        """Consume and return the current token."""
        if self._pos >= self._len:
            raise UnexpectedEndError
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def accept(self, kind: TokenKind[Any]) -> bool:
        """Consume the current token if it is of the given kind."""
        token = self.peek()
        if token is None or token.kind is not kind:
            return False
        self._pos += 1
        return True

    def expect(self, kind: TokenKind[T]) -> T:
        """Consume the current token of the given kind and get its value."""
        token = self.advance()
        if token.kind is not kind:
            raise UnexpectedTokenError(token.text)
        return kind.value(token)
