"""Entry filters."""
import re
from datetime import date
from typing import Any
from typing import Callable
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

import ply.yacc  # type: ignore
from beancount.core import account
from beancount.core.data import Directive
from beancount.core.data import Entries
from beancount.ops.summarize import clamp_opt  # type: ignore

from fava.core.accounts import get_entry_accounts
from fava.core.fava_options import FavaOptions
from fava.helpers import FavaAPIException
from fava.util.date import parse_date
from fava.util.typing import BeancountOptions


class FilterException(FavaAPIException):
    """Filter exception."""

    def __init__(self, filter_type: str, message: str) -> None:
        super().__init__(message)
        self.filter_type = filter_type

    def __str__(self) -> str:
        return self.message


class Token:
    """A token having a certain type and value.

    The lexer attribute only exists since PLY writes to it in case of a parser
    error.
    """

    __slots__ = ["type", "value", "lexer"]

    def __init__(self, type_: str, value: str) -> None:
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value})"


class FilterSyntaxLexer:
    """Lexer for Fava's filter syntax."""

    # pylint: disable=missing-docstring,invalid-name,no-self-use

    tokens = ("ANY", "ALL", "KEY", "LINK", "STRING", "TAG")

    RULES = (
        ("LINK", r"\^[A-Za-z0-9\-_/.]+"),
        ("TAG", r"\#[A-Za-z0-9\-_/.]+"),
        ("KEY", r"[a-z][a-zA-Z0-9\-_]+:"),
        ("ALL", r"all\("),
        ("ANY", r"any\("),
        ("STRING", r'\w[-\w]*|"[^"]*"|\'[^\']*\''),
    )

    regex = re.compile(
        "|".join((f"(?P<{name}>{rule})" for name, rule in RULES))
    )

    def LINK(self, token: str, value: str) -> Tuple[str, str]:
        return token, value[1:]

    def TAG(self, token: str, value: str) -> Tuple[str, str]:
        return token, value[1:]

    def KEY(self, token: str, value: str) -> Tuple[str, str]:
        return token, value[:-1]

    def ALL(self, token: str, _: str) -> Tuple[str, str]:
        return token, token

    def ANY(self, token: str, _: str) -> Tuple[str, str]:
        return token, token

    def STRING(self, token: str, value: str) -> Tuple[str, str]:
        if value[0] in ['"', "'"]:
            return token, value[1:-1]
        return token, value

    def lex(self, data: str) -> Generator[Token, None, None]:
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
                assert token is not None, "Internal Error"
                func: Callable[[str, str], Tuple[str, str]] = getattr(
                    self, token
                )
                ret = func(token, value)
                yield Token(*ret)
            elif char in literals:
                yield Token(char, char)
                pos += 1
            else:
                raise FilterException(
                    "filter", f'Illegal character "{char}" in filter.'
                )


class Match:
    """Match a string."""

    __slots__ = ["match"]

    def __init__(self, search: str) -> None:
        try:
            match = re.compile(search, re.IGNORECASE).search
            self.match: Callable[[str], bool] = lambda s: bool(match(s))
        except re.error:
            self.match = lambda s: s == search

    def __call__(self, string: str) -> bool:
        return self.match(string)


class FilterSyntaxParser:
    # pylint: disable=missing-docstring,invalid-name,no-self-use

    precedence = (("left", "AND"), ("right", "UMINUS"))
    tokens = FilterSyntaxLexer.tokens

    def p_error(self, _: Any) -> None:
        raise FilterException("filter", "Failed to parse filter: ")

    def p_filter(self, p: List[Any]) -> None:
        """
        filter : expr
        """
        p[0] = p[1]

    def p_expr(self, p: List[Any]) -> None:
        """
        expr : simple_expr
        """
        p[0] = p[1]

    def p_expr_all(self, p: List[Any]) -> None:
        """
        expr : ALL expr ')'
        """
        expr = p[2]

        def _match_postings(entry: Directive) -> bool:
            return all(
                expr(posting) for posting in getattr(entry, "postings", [])
            )

        p[0] = _match_postings

    def p_expr_any(self, p: List[Any]) -> None:
        """
        expr : ANY expr ')'
        """
        expr = p[2]

        def _match_postings(entry: Directive) -> bool:
            return any(
                expr(posting) for posting in getattr(entry, "postings", [])
            )

        p[0] = _match_postings

    def p_expr_parentheses(self, p: List[Any]) -> None:
        """
        expr : '(' expr ')'
        """
        p[0] = p[2]

    def p_expr_and(self, p: List[Any]) -> None:
        """
        expr : expr expr %prec AND
        """
        left, right = p[1], p[2]

        def _and(entry: Directive) -> bool:
            return left(entry) and right(entry)  # type: ignore

        p[0] = _and

    def p_expr_or(self, p: List[Any]) -> None:
        """
        expr : expr ',' expr
        """
        left, right = p[1], p[3]

        def _or(entry: Directive) -> bool:
            return left(entry) or right(entry)  # type: ignore

        p[0] = _or

    def p_expr_negated(self, p: List[Any]) -> None:
        """
        expr : '-' expr %prec UMINUS
        """
        func = p[2]

        def _neg(entry: Directive) -> bool:
            return not func(entry)

        p[0] = _neg

    def p_simple_expr_TAG(self, p: List[Any]) -> None:
        """
        simple_expr : TAG
        """
        tag = p[1]

        def _tag(entry: Directive) -> bool:
            tags = getattr(entry, "tags", None)
            return (tag in tags) if tags is not None else False

        p[0] = _tag

    def p_simple_expr_LINK(self, p: List[Any]) -> None:
        """
        simple_expr : LINK
        """
        link = p[1]

        def _link(entry: Directive) -> bool:
            links = getattr(entry, "links", None)
            return (link in links) if links is not None else False

        p[0] = _link

    def p_simple_expr_STRING(self, p: List[Any]) -> None:
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

    def p_simple_expr_key(self, p: List[Any]) -> None:
        """
        simple_expr : KEY STRING
        """
        key, value = p[1], p[2]
        match = Match(value)

        def _key(entry: Directive) -> bool:
            if hasattr(entry, key):
                return match(str(getattr(entry, key) or ""))
            if entry.meta is not None and key in entry.meta:
                return match(str(entry.meta.get(key)))
            return False

        p[0] = _key


class EntryFilter:
    """Filters a list of entries."""

    def __init__(
        self, options: BeancountOptions, fava_options: FavaOptions
    ) -> None:
        self.options = options
        self.fava_options = fava_options
        self.value: Optional[str] = None

    def set(self, value: Optional[str]) -> bool:
        """Set the filter.

        Subclasses should check for validity of the value in this method.
        """
        if value == self.value:
            return False
        self.value = value
        return True

    def _include_entry(self, entry: Directive) -> bool:
        raise NotImplementedError

    def _filter(self, entries: Entries) -> Entries:
        return [entry for entry in entries if self._include_entry(entry)]

    def apply(self, entries: Entries) -> Entries:
        """Apply filter.

        Args:
            entries: a list of entries.
            options: an options_map.

        Returns:
            A list of filtered entries.
        """
        if self.value:
            return self._filter(entries)
        return entries

    def __bool__(self) -> bool:
        return bool(self.value)


class TimeFilter(EntryFilter):  # pylint: disable=abstract-method
    """Filter by dates."""

    def __init__(
        self, options: BeancountOptions, fava_options: FavaOptions
    ) -> None:
        super().__init__(options, fava_options)
        self.begin_date: Optional[date] = None
        self.end_date: Optional[date] = None

    def set(self, value: Optional[str]) -> bool:
        if value == self.value:
            return False
        self.value = value
        if not self.value:
            return True

        self.begin_date, self.end_date = parse_date(
            self.value, self.fava_options["fiscal-year-end"]
        )
        if not self.begin_date:
            self.value = None
            raise FilterException("time", f"Failed to parse date: {value}")
        return True

    def _filter(self, entries: Entries) -> Entries:
        entries, _ = clamp_opt(
            entries, self.begin_date, self.end_date, self.options
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

    def __init__(
        self, options: BeancountOptions, fava_options: FavaOptions
    ) -> None:
        super().__init__(options, fava_options)
        self._include = None

    def set(self, value: Optional[str]) -> bool:
        if value == self.value:
            return False
        self.value = value
        if value and value.strip():
            try:
                tokens = LEXER.lex(value.strip())
                self._include = PARSE(
                    lexer="NONE",
                    tokenfunc=lambda toks=tokens: next(toks, None),
                )
            except FilterException as exception:
                exception.message = exception.message + value
                self.value = None
                raise exception
        else:
            self._include = None
        return True

    def _include_entry(self, entry: Directive) -> bool:
        if self._include:
            return self._include(entry)
        return True


class AccountFilter(EntryFilter):
    """Filter by account.

    The filter string can either a regular expression or a parent account.
    """

    def __init__(
        self, options: BeancountOptions, fava_options: FavaOptions
    ) -> None:
        super().__init__(options, fava_options)
        self.match: Optional[Match] = None

    def set(self, value: Optional[str]) -> bool:
        if value == self.value:
            return False
        self.value = value
        self.match = Match(value or "")
        return True

    def _include_entry(self, entry: Directive) -> bool:
        if self.value is None or self.match is None:
            return False
        return any(
            account.has_component(name, self.value) or self.match(name)
            for name in get_entry_accounts(entry)
        )
