"""Entry filters."""

from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from decimal import Decimal
from typing import Any
from typing import Callable
from typing import TYPE_CHECKING

import ply.yacc  # type: ignore[import-untyped]
from beancount.core import account
from beancount.ops.summarize import clamp_opt  # type: ignore[import-untyped]

from fava.beans.account import get_entry_accounts
from fava.helpers import FavaAPIError
from fava.util.date import DateRange
from fava.util.date import parse_date

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Sequence

    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions
    from fava.core.fava_options import FavaOptions


class FilterError(FavaAPIError):
    """Filter exception."""

    def __init__(self, filter_type: str, message: str) -> None:
        super().__init__(message)
        self.filter_type = filter_type

    def __str__(self) -> str:
        return self.message


class FilterParseError(FilterError):
    """Filter parse error."""

    def __init__(self) -> None:
        super().__init__("filter", "Failed to parse filter: ")


class FilterIllegalCharError(FilterError):
    """Filter illegal char error."""

    def __init__(self, char: str) -> None:
        super().__init__(
            "filter",
            f'Illegal character "{char}" in filter.',
        )


class TimeFilterParseError(FilterError):
    """Time filter parse error."""

    def __init__(self, value: str) -> None:
        super().__init__("time", f"Failed to parse date: {value}")


class Token:
    """A token having a certain type and value.

    The lexer attribute only exists since PLY writes to it in case of a parser
    error.
    """

    __slots__ = ("lexer", "type", "value")

    def __init__(self, type_: str, value: str) -> None:
        self.type = type_
        self.value = value

    def __repr__(self) -> str:  # pragma: no cover
        return f"Token({self.type}, {self.value})"


class FilterSyntaxLexer:
    """Lexer for Fava's filter syntax."""

    tokens = (
        "ANY",
        "ALL",
        "CMP_OP",
        "EQ_OP",
        "KEY",
        "LINK",
        "NUMBER",
        "STRING",
        "TAG",
    )

    RULES = (
        ("LINK", r"\^[A-Za-z0-9\-_/.]+"),
        ("TAG", r"\#[A-Za-z0-9\-_/.]+"),
        ("ALL", r"all\("),
        ("ANY", r"any\("),
        ("KEY", r"[a-z][a-zA-Z0-9\-_]+(?=\s*(:|=|>=|<=|<|>))"),
        ("EQ_OP", r":"),
        ("CMP_OP", r"(=|>=|<=|<|>)"),
        ("NUMBER", r"\d*\.?\d+"),
        ("STRING", r"""\w[-\w]*|"[^"]*"|'[^']*'"""),
    )

    regex = re.compile(
        "|".join((f"(?P<{name}>{rule})" for name, rule in RULES)),
    )

    def LINK(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        return token, value[1:]

    def TAG(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        return token, value[1:]

    def KEY(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        return token, value

    def ALL(self, token: str, _: str) -> tuple[str, str]:  # noqa: N802
        return token, token

    def ANY(self, token: str, _: str) -> tuple[str, str]:  # noqa: N802
        return token, token

    def EQ_OP(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        return token, value

    def CMP_OP(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        return token, value

    def NUMBER(self, token: str, value: str) -> tuple[str, Decimal]:  # noqa: N802
        return token, Decimal(value)

    def STRING(self, token: str, value: str) -> tuple[str, str]:  # noqa: N802
        if value[0] in {'"', "'"}:
            return token, value[1:-1]
        return token, value

    def lex(self, data: str) -> Iterable[Token]:
        """A generator yielding all tokens in a given line.

        Arguments:
            data: A string, the line to lex.

        Yields:
            All Tokens in the line.
        """
        ignore = " \t"
        literals = "-,()"
        regex = self.regex.match

        pos = 0
        length = len(data)
        while pos < length:
            char = data[pos]
            if char in ignore:
                pos += 1
                continue
            match = regex(data, pos)
            if match:
                value = match.group()
                pos += len(value)
                token = match.lastgroup
                if token is None:  # pragma: no cover
                    msg = "Internal Error"
                    raise ValueError(msg)
                func: Callable[[str, str], tuple[str, str]] = getattr(
                    self,
                    token,
                )
                ret = func(token, value)
                yield Token(*ret)
            elif char in literals:
                yield Token(char, char)
                pos += 1
            else:
                raise FilterIllegalCharError(char)


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
        # Compare to the absolute value to simplify this filter.
        number = getattr(obj, "number", None)
        return self.match(abs(number)) if number is not None else False


class FilterSyntaxParser:
    precedence = (("left", "AND"), ("right", "UMINUS"))
    tokens = FilterSyntaxLexer.tokens

    def p_error(self, _: Any) -> None:
        raise FilterParseError

    def p_filter(self, p: list[Any]) -> None:
        """
        filter : expr
        """
        p[0] = p[1]

    def p_expr(self, p: list[Any]) -> None:
        """
        expr : simple_expr
        """
        p[0] = p[1]

    def p_expr_all(self, p: list[Any]) -> None:
        """
        expr : ALL expr ')'
        """
        expr = p[2]

        def _match_postings(entry: Directive) -> bool:
            return all(
                expr(posting) for posting in getattr(entry, "postings", [])
            )

        p[0] = _match_postings

    def p_expr_any(self, p: list[Any]) -> None:
        """
        expr : ANY expr ')'
        """
        expr = p[2]

        def _match_postings(entry: Directive) -> bool:
            return any(
                expr(posting) for posting in getattr(entry, "postings", [])
            )

        p[0] = _match_postings

    def p_expr_parentheses(self, p: list[Any]) -> None:
        """
        expr : '(' expr ')'
        """
        p[0] = p[2]

    def p_expr_and(self, p: list[Any]) -> None:
        """
        expr : expr expr %prec AND
        """
        left, right = p[1], p[2]

        def _and(entry: Directive) -> bool:
            return left(entry) and right(entry)  # type: ignore[no-any-return]

        p[0] = _and

    def p_expr_or(self, p: list[Any]) -> None:
        """
        expr : expr ',' expr
        """
        left, right = p[1], p[3]

        def _or(entry: Directive) -> bool:
            return left(entry) or right(entry)  # type: ignore[no-any-return]

        p[0] = _or

    def p_expr_negated(self, p: list[Any]) -> None:
        """
        expr : '-' expr %prec UMINUS
        """
        func = p[2]

        def _neg(entry: Directive) -> bool:
            return not func(entry)

        p[0] = _neg

    def p_simple_expr_TAG(self, p: list[Any]) -> None:  # noqa: N802
        """
        simple_expr : TAG
        """
        tag = p[1]

        def _tag(entry: Directive) -> bool:
            tags = getattr(entry, "tags", None)
            return (tag in tags) if tags is not None else False

        p[0] = _tag

    def p_simple_expr_LINK(self, p: list[Any]) -> None:  # noqa: N802
        """
        simple_expr : LINK
        """
        link = p[1]

        def _link(entry: Directive) -> bool:
            links = getattr(entry, "links", None)
            return (link in links) if links is not None else False

        p[0] = _link

    def p_simple_expr_STRING(self, p: list[Any]) -> None:  # noqa: N802
        """
        simple_expr : STRING
        """
        string = p[1]
        match = Match(string)

        def _string(entry: Directive) -> bool:
            for name in ("narration", "payee", "comment"):
                value = getattr(entry, name, "")
                if value and match(value):
                    return True
            return False

        p[0] = _string

    def p_simple_expr_key(self, p: list[Any]) -> None:
        """
        simple_expr : KEY EQ_OP STRING
                    | KEY CMP_OP NUMBER
        """
        key, op, value = p[1], p[2], p[3]
        match: Match | MatchAmount = (
            Match(value) if op == ":" else MatchAmount(op, value)
        )

        def _key(entry: Directive) -> bool:
            if hasattr(entry, key):
                return match(getattr(entry, key) or "")
            if entry.meta is not None and key in entry.meta:
                return match(entry.meta.get(key))
            return False

        p[0] = _key

    def p_simple_expr_units(self, p: list[Any]) -> None:
        """
        simple_expr : CMP_OP NUMBER
        """
        op, value = p[1], p[2]
        match = MatchAmount(op, value)

        def _range(entry: Directive) -> bool:
            return any(
                match(posting.units)
                for posting in getattr(entry, "postings", [])
            )

        p[0] = _range


class EntryFilter(ABC):
    """Filters a list of entries."""

    @abstractmethod
    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        """Filter a list of directives."""


class TimeFilter(EntryFilter):
    """Filter by dates."""

    __slots__ = ("_options", "date_range")

    def __init__(
        self,
        options: BeancountOptions,
        fava_options: FavaOptions,
        value: str,
    ) -> None:
        self._options = options
        begin, end = parse_date(value, fava_options.fiscal_year_end)
        if not begin or not end:
            raise TimeFilterParseError(value)
        self.date_range = DateRange(begin, end)

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        entries, _ = clamp_opt(
            entries,
            self.date_range.begin,
            self.date_range.end,
            self._options,
        )
        return entries


LEXER = FilterSyntaxLexer()
PARSE = ply.yacc.yacc(
    errorlog=ply.yacc.NullLogger(),
    write_tables=False,
    debug=False,
    module=FilterSyntaxParser(),
).parse


class AdvancedFilter(EntryFilter):
    """Filter by tags and links and keys."""

    __slots__ = ("_include",)

    def __init__(self, value: str) -> None:
        try:
            tokens = LEXER.lex(value)
            self._include = PARSE(
                lexer="NONE",
                tokenfunc=lambda toks=tokens: next(toks, None),
            )
        except FilterError as exception:
            exception.message += value
            raise

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        include = self._include
        return [entry for entry in entries if include(entry)]


class AccountFilter(EntryFilter):
    """Filter by account.

    The filter string can either be a regular expression or a parent account.
    """

    __slots__ = ("_match", "_value")

    def __init__(self, value: str) -> None:
        self._value = value
        self._match = Match(value)

    def apply(self, entries: Sequence[Directive]) -> Sequence[Directive]:
        value = self._value
        if not value:
            return entries
        match = self._match
        return [
            entry
            for entry in entries
            if any(
                account.has_component(name, value) or match(name)
                for name in get_entry_accounts(entry)
            )
        ]
