"""Parsing of the date expressions that Fava's time filter supports.

See :func:`parse_date` for the supported syntax.
"""

from __future__ import annotations

import datetime
import re
from datetime import timedelta
from typing import Literal
from typing import TYPE_CHECKING

from fava.util.date import DateRange
from fava.util.date import Day
from fava.util.date import END_OF_YEAR
from fava.util.date import FiscalQuarter
from fava.util.date import FiscalYear
from fava.util.date import InvalidDateRangeError
from fava.util.date import local_today
from fava.util.date import Month
from fava.util.date import month_offset
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
    flags=re.IGNORECASE,
)


class Period:
    """A period given by its first day and the interval that it spans."""

    def __init__(self, begin: datetime.date, interval: Interval) -> None:
        self.begin = begin
        self.interval = interval

    @property
    def date_range(self) -> DateRange:
        """The range of dates that this period spans."""
        return DateRange(self.begin, self.interval.get_next(self.begin))

    def refine(self, token: Token) -> Period:
        """Narrow this period down, e.g. a year to one of its months."""
        raise UnexpectedTokenError(token.text)


class YearPeriod(Period):
    """A calendar year, which can be refined to a month, quarter or week."""

    def __init__(self, year: int) -> None:
        super().__init__(datetime.date(year, 1, 1), Year)

    @override
    def refine(self, token: Token) -> Period:
        year = self.begin.year
        if token.kind is NUMBER:
            return MonthPeriod(year, NUMBER.value(token))
        if token.kind is QUARTER:
            month = (QUARTER.value(token) - 1) * 3 + 1
            return Period(datetime.date(year, month, 1), Quarter)
        if token.kind is WEEK:
            begin = datetime.date.fromisocalendar(year, WEEK.value(token), 1)
            return Period(begin, Week)
        raise UnexpectedTokenError(token.text)


class MonthPeriod(Period):
    """A month, which can be refined to one of its days."""

    def __init__(self, year: int, month: int) -> None:
        super().__init__(datetime.date(year, month, 1), Month)

    @override
    def refine(self, token: Token) -> Period:
        if token.kind is NUMBER:
            begin = datetime.date(
                self.begin.year, self.begin.month, NUMBER.value(token)
            )
            return Period(begin, Day)
        raise UnexpectedTokenError(token.text)


class FiscalYearPeriod(Period):
    """A fiscal year, which can be refined to one of its quarters."""

    interval: FiscalYear

    def __init__(self, begin: datetime.date, fye: FiscalYearEnd) -> None:
        super().__init__(begin, FiscalYear(fye))

    @override
    def refine(self, token: Token) -> Period:
        if token.kind is QUARTER:
            fiscal_quarter = FiscalQuarter(self.interval.fye)
            begin = month_offset(self.begin, (QUARTER.value(token) - 1) * 3)
            return Period(begin, fiscal_quarter)
        raise UnexpectedTokenError(token.text)


def _period_for_variable(  # noqa: PLR0911
    name: Variable, offset: int, fye: FiscalYearEnd
) -> Period:
    """The period that a variable like 'month+2' refers to."""
    today = local_today()
    if name == "fiscal_year":
        fiscal_year = FiscalYear(fye)
        cur = fiscal_year.get_prev(today)
        return FiscalYearPeriod(cur.replace(year=cur.year + offset), fye)
    if name == "fiscal_quarter":
        fiscal_quarter = FiscalQuarter(fye)
        begin = month_offset(fiscal_quarter.get_prev(today), offset * 3)
        return Period(begin, fiscal_quarter)
    if name == "year":
        return YearPeriod(today.year + offset)
    if name == "quarter":
        begin = month_offset(Quarter.get_prev(today), offset * 3)
        return Period(begin, Quarter)
    if name == "month":
        begin = month_offset(Month.get_prev(today), offset)
        return MonthPeriod(begin.year, begin.month)
    if name == "week":
        return Period(Week.get_prev(today) + timedelta(offset * 7), Week)
    assert_type(name, Literal["day"])
    return Period(today + timedelta(offset), Day)


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
        date_range = self._period().date_range
        if self._at_separator():
            self.advance()
            end = self._period().date_range.end
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

    def _period(self) -> Period:
        """Parse a single period, like '2010-03' or '(month)-10'."""
        token = self.advance()
        if token.kind is YEAR:
            period: Period = YearPeriod(YEAR.value(token))
        elif token.kind is FY:
            begin = self._fye.begin_date_for_year(FY.value(token))
            period = FiscalYearPeriod(begin, self._fye)
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

    def _variable(self, name: Variable) -> Period:
        """Parse the optional offset of a variable and evaluate it."""
        offset = 0
        if (sign := self.peek_kind()) in (DASH, PLUS) and self.peek_kind(
            1
        ) is NUMBER:
            self.advance()
            number = self.expect(NUMBER)
            offset = number if sign is PLUS else -number
        return _period_for_variable(name, offset, self._fye)


def parse_date(string: str, fye: FiscalYearEnd = END_OF_YEAR) -> DateRange:
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
        The range of dates.

    Raises:
        ParseError: If parsing the string failed.
        InvalidDateRangeError: For an invalid date range, e.g. '2012 - 2010'
    """
    try:
        return _DateExpressionParser(string, fye).parse()
    except ValueError as error:
        if isinstance(error, (ParseError, InvalidDateRangeError)):
            raise
        # Errors from a date creation or similar (e.g. invalid month)
        raise NoSuchPeriodError from error
