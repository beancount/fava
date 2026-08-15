"""Parsing of the date expressions that Fava's time filter supports.

See :func:`parse_date` for the supported syntax.
"""

from __future__ import annotations

import datetime
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Literal
from typing import TYPE_CHECKING

from fava.util.date import DateRange
from fava.util.date import Day
from fava.util.date import END_OF_YEAR
from fava.util.date import FyeHasNoQuartersError
from fava.util.date import get_fiscal_period
from fava.util.date import InvalidDateRangeError
from fava.util.date import local_today
from fava.util.date import Month
from fava.util.date import Quarter
from fava.util.date import Week
from fava.util.date import Year
from fava.util.parsing import KeywordTokenKind
from fava.util.parsing import Lexer
from fava.util.parsing import LiteralTokenKind
from fava.util.parsing import ParseError
from fava.util.parsing import ParserBase
from fava.util.parsing import TokenKind
from fava.util.parsing import UnexpectedTokenError

try:
    from typing import assert_type
    from typing import override  # pragma: no cover
except ImportError:  # pragma: no cover
    from typing_extensions import assert_type
    from typing_extensions import override

if TYPE_CHECKING:  # pragma: no cover
    from fava.util.date import FiscalYearEnd
    from fava.util.date import Interval
    from fava.util.parsing import Token


class NoSuchPeriodError(ParseError):
    """A date expression is valid syntax but denotes no existing period.

    This covers dates that do not exist, like the 30th of February or week
    99, years outside the range that dates support, and fiscal quarters for
    a fiscal year end that does not have any.
    """

    def __init__(self) -> None:
        super().__init__(
            "Date expression denotes a period that does not exist."
        )


#: The variables that denote a period around the current day.
Variable = Literal[
    "fiscal_year",
    "fiscal_quarter",
    "year",
    "quarter",
    "month",
    "week",
    "day",
]

FY = TokenKind(r"fy\d{4}", lambda s: int(s[2:]))
YEAR = TokenKind(r"\d{4}", int)
VARIABLE: KeywordTokenKind[Variable] = KeywordTokenKind(Variable)
QUARTER = TokenKind(r"q[1-4]", lambda s: int(s[1:]))
WEEK = TokenKind(r"w\d{2}", lambda s: int(s[1:]))
NUMBER = TokenKind(r"\d{1,3}", int)
PLUS = LiteralTokenKind("+")
DASH = LiteralTokenKind("-")
OPEN = LiteralTokenKind("(")
CLOSE = LiteralTokenKind(")")

#: The lexer for date expressions.
_LEXER = Lexer(
    (FY, YEAR, VARIABLE, QUARTER, WEEK, NUMBER, PLUS, DASH, OPEN, CLOSE),
    re.IGNORECASE,
)


def _make_date(year: int, month: int, day: int) -> datetime.date:
    """Build a date, for a date that does not exist raise an error."""
    try:
        return datetime.date(year, month, day)
    except ValueError as err:
        raise NoSuchPeriodError from err


def _iso_week_start(year: int, week: int) -> datetime.date:
    """The Monday of the given week of the ISO week-based year."""
    try:
        return (
            datetime.datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%w")
            .replace(tzinfo=datetime.timezone.utc)
            .date()
        )
    except ValueError as err:
        raise NoSuchPeriodError from err


class _Period(ABC):
    """A period of time that (part of) a date expression denotes."""

    @abstractmethod
    def date_range(self, fye: FiscalYearEnd) -> DateRange:
        """The range of dates that this period spans."""

    def refine(self, token: Token) -> _Period:
        """Narrow this period down, e.g. a year to one of its months."""
        raise UnexpectedTokenError(token.text)


@dataclass(frozen=True)
class _IntervalPeriod(_Period):
    """A period given by its first day and the interval that it spans."""

    begin: datetime.date
    interval: Interval

    @override
    def date_range(self, fye: FiscalYearEnd) -> DateRange:
        return DateRange(self.begin, self.interval.get_next(self.begin))


@dataclass(frozen=True)
class _YearPeriod(_Period):
    """A calendar year, which can be refined to a month, quarter or week."""

    year: int

    @override
    def date_range(self, fye: FiscalYearEnd) -> DateRange:
        begin = _make_date(self.year, 1, 1)
        return DateRange(begin, Year.get_next(begin))

    @override
    def refine(self, token: Token) -> _Period:
        if token.kind is NUMBER:
            return _MonthPeriod(self.year, NUMBER.value(token))
        if token.kind is QUARTER:
            month = (QUARTER.value(token) - 1) * 3 + 1
            return _IntervalPeriod(_make_date(self.year, month, 1), Quarter)
        if token.kind is WEEK:
            begin = _iso_week_start(self.year, WEEK.value(token))
            return _IntervalPeriod(begin, Week)
        raise UnexpectedTokenError(token.text)


@dataclass(frozen=True)
class _MonthPeriod(_Period):
    """A month, which can be refined to one of its days."""

    year: int
    month: int

    @override
    def date_range(self, fye: FiscalYearEnd) -> DateRange:
        begin = _make_date(self.year, self.month, 1)
        return DateRange(begin, Month.get_next(begin))

    @override
    def refine(self, token: Token) -> _Period:
        if token.kind is NUMBER:
            begin = _make_date(self.year, self.month, NUMBER.value(token))
            return _IntervalPeriod(begin, Day)
        raise UnexpectedTokenError(token.text)


@dataclass(frozen=True)
class _FiscalYearPeriod(_Period):
    """A fiscal year, which can be refined to one of its quarters."""

    year: int
    quarter: int | None = None

    @override
    def date_range(self, fye: FiscalYearEnd) -> DateRange:
        try:
            begin, end = get_fiscal_period(self.year, fye, self.quarter)
        except ValueError as err:  # the year is out of range
            raise NoSuchPeriodError from err
        if begin is None or end is None:  # the fye has no quarters
            raise NoSuchPeriodError
        return DateRange(begin, end)

    @override
    def refine(self, token: Token) -> _Period:
        if token.kind is QUARTER and self.quarter is None:
            return _FiscalYearPeriod(self.year, QUARTER.value(token))
        raise UnexpectedTokenError(token.text)


def _period_for_variable(  # noqa: PLR0911
    name: Variable,
    offset: int,
    fye: FiscalYearEnd,
) -> _Period:
    """The period that a variable like 'month+2' refers to."""
    today = local_today()
    if name == "fiscal_year":
        after_fye = (today.month, today.day) > (fye.month_of_year, fye.day)
        year = today.year + (1 if after_fye else 0) - fye.year_offset
        return _FiscalYearPeriod(year + offset)
    if name == "fiscal_quarter":
        if not fye.has_quarters():
            raise FyeHasNoQuartersError
        # Do not build a date for the offset month - the year might well be
        # out of range, which is detected when the date range is computed.
        year_delta, month_index = divmod(today.month - 1 + offset * 3, 12)
        month = month_index + 1
        after_fye = month > fye.month_of_year
        year = today.year + year_delta - fye.year_offset
        quarter = ((month - fye.month_of_year - 1) // 3) % 4 + 1
        return _FiscalYearPeriod(year + (1 if after_fye else 0), quarter)
    if name == "year":
        return _YearPeriod(today.year + offset)
    if name == "quarter":
        quarter_today = (today.month - 1) // 3 + 1
        year = today.year + (quarter_today + offset - 1) // 4
        quarter = (quarter_today + offset - 1) % 4 + 1
        month = (quarter - 1) * 3 + 1
        return _IntervalPeriod(_make_date(year, month, 1), Quarter)
    if name == "month":
        year = today.year + (today.month + offset - 1) // 12
        month = (today.month + offset - 1) % 12 + 1
        return _MonthPeriod(year, month)
    if name == "week":
        return _IntervalPeriod(
            Week.get_prev(today + timedelta(offset * 7)), Week
        )
    assert_type(name, Literal["day"])
    return _IntervalPeriod(today + timedelta(offset), Day)


class _DateExpressionParser(ParserBase):
    """A parser for Fava's date expressions.

    The grammar is roughly the following, with the caveat that a '-' is only
    a range separator if it is followed by the start of another period::

        expression := period ['-' period]
        period     := atom {'-' refinement}
        atom       := YEAR | FY | variable | '(' variable ')'
        variable   := VARIABLE [('+' | '-') NUMBER]
        refinement := NUMBER | QUARTER | WEEK
    """

    def __init__(self, string: str, fye: FiscalYearEnd) -> None:
        super().__init__(tuple(_LEXER.tokenize(string)))
        self._fye = fye

    def parse(self) -> DateRange:
        """Parse the whole expression into a date range."""
        date_range = self._period().date_range(self._fye)
        if self._at_separator():
            self.advance()
            end = self._period().date_range(self._fye).end
            date_range = DateRange(date_range.begin, end)
        if remaining := self.peek():
            raise UnexpectedTokenError(remaining.text)
        return date_range

    def _at_separator(self) -> bool:
        """Whether the current token separates the two ends of a range."""
        return self.peek_kind() is DASH and self.peek_kind(1) in (
            FY,
            OPEN,
            VARIABLE,
            YEAR,
        )

    def _period(self) -> _Period:
        """Parse a single period, like '2010-03' or '(month)-10'."""
        token = self.advance()
        if token.kind is YEAR:
            period: _Period = _YearPeriod(YEAR.value(token))
        elif token.kind is FY:
            period = _FiscalYearPeriod(FY.value(token))
        elif token.kind is VARIABLE:
            period = self._variable(VARIABLE.value(token))
        elif token.kind is OPEN:
            period = self._variable(self.expect(VARIABLE))
            self.expect(CLOSE)
        else:
            raise UnexpectedTokenError(token.text)

        while self.peek_kind() is DASH and not self._at_separator():
            self.advance()
            period = period.refine(self.advance())
        return period

    def _variable(self, name: Variable) -> _Period:
        """Parse the optional offset of a variable and evaluate it."""
        offset = 0
        if (sign := self.peek_kind()) in (DASH, PLUS) and self.peek_kind(
            1
        ) is NUMBER:
            self.advance()
            number = self.expect(NUMBER)
            offset = number if sign is PLUS else -number
        try:
            return _period_for_variable(name, offset, self._fye)
        except FyeHasNoQuartersError as err:
            raise NoSuchPeriodError from err


def parse_date(
    string: str,
    fye: FiscalYearEnd | None = None,
) -> DateRange | None:
    """Parse a date.

    Example of supported formats:

    - 2010-03-15, 2010-03, 2010
    - 2010-W01, 2010-Q3
    - FY2012, FY2012-Q2

    Instead of a year, month, etc., one of the variables 'year', 'quarter',
    'month', 'week', 'day', 'fiscal_year' and 'fiscal_quarter' can be used to
    refer to the period around the current day. They support addition and
    subtraction of an offset of up to three digits, e.g. 'month-2' - four
    digits are a year and hence start a range. To subtract from the *date*
    instead of shifting the period, put the variable in parentheses -
    'month-10' is ten months ago whereas '(month)-10' is the tenth of the
    current month.

    A range of dates can be expressed as 'start - end', where start and end
    look like one of the above examples.

    Args:
        string: A date(range) in our custom format.
        fye: The fiscal year end to consider.

    Returns:
        The range of dates - None if it could not be parsed or if it does
        not span at least one day.
    """
    try:
        return _DateExpressionParser(string, fye or END_OF_YEAR).parse()
    except (ParseError, OverflowError, InvalidDateRangeError):
        return None
