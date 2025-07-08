"""Date-related functionality.

Note:
    Date ranges are always tuples (start, end) from the (inclusive) start date
    to the (exclusive) end date.
"""

from __future__ import annotations

import datetime
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from itertools import tee
from typing import TYPE_CHECKING

from flask_babel import gettext

from fava.util import listify

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Iterator


IS_RANGE_RE = re.compile(r"(.*?)(?:-|to)(?=\s*(?:fy)*\d{4})(.*)")

# these match dates of the form 'year-month-day'
# day or month and day may be omitted
YEAR_RE = re.compile(r"^\d{4}$")
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")
DAY_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# this matches a week like 2016-W02 for the second week of 2016
WEEK_RE = re.compile(r"^(\d{4})-w(\d{2})$")

# this matches a quarter like 2016-Q1 for the first quarter of 2016
QUARTER_RE = re.compile(r"^(\d{4})-q([1234])$")

# this matches a financial year like FY2018 for the financial year ending 2018
FY_RE = re.compile(r"^fy(\d{4})$")

# this matches a quarter in a financial year like FY2018-Q2
FY_QUARTER_RE = re.compile(r"^fy(\d{4})-q([1234])$")

VARIABLE_RE = re.compile(
    r"\(?(fiscal_year|year|fiscal_quarter|quarter"
    r"|month|week|day)(?:([-+])(\d+))?\)?",
)


@dataclass(frozen=True)
class FiscalYearEnd:
    """Month and day that specify the end of the fiscal year."""

    month: int
    day: int

    @property
    def month_of_year(self) -> int:
        """Actual month of the year."""
        return (self.month - 1) % 12 + 1

    @property
    def year_offset(self) -> int:
        """Number of years that this is offset into the future."""
        return (self.month - 1) // 12

    def has_quarters(self) -> bool:
        """Whether this fiscal year end supports fiscal quarters."""
        return (
            datetime.date(2001, self.month_of_year, self.day) + ONE_DAY
        ).day == 1


class FyeHasNoQuartersError(ValueError):
    """Only fiscal year that start on the first of a month have quarters."""

    def __init__(self) -> None:
        super().__init__(
            "Cannot use fiscal quarter if fiscal year "
            "does not start on first of the month"
        )


END_OF_YEAR = FiscalYearEnd(12, 31)


class Interval(ABC):
    """An interval."""

    @property
    @abstractmethod
    def label(self) -> str:
        """The label for the interval."""

    @abstractmethod
    def format_date(self, date: datetime.date) -> str:
        """Format a date for this interval for the Fava time filter."""

    @abstractmethod
    def get_prev(self, date: datetime.date) -> datetime.date:
        """Get the start date of the interval in which the date falls."""

    @abstractmethod
    def get_next(self, date: datetime.date) -> datetime.date:
        """Get the start date of the next interval following the date."""

    def number_of_days(self, date: datetime.date) -> int:
        """Get number of days in the surrounding interval."""
        start = self.get_prev(date)
        end = self.get_next(start)
        return (end - start).days


class _IntervalYear(Interval):
    """A year interval."""

    @property
    def label(self) -> str:
        return gettext("Yearly")

    def format_date(self, date: datetime.date) -> str:
        return date.strftime("%Y")

    def get_prev(self, date: datetime.date) -> datetime.date:
        return datetime.date(date.year, 1, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return datetime.date(date.year + 1, 1, 1)
        except ValueError:
            return datetime.date.max


class _IntervalQuarter(Interval):
    """A quarter interval."""

    @property
    def label(self) -> str:
        return gettext("Quarterly")

    def format_date(self, date: datetime.date) -> str:
        return f"{date.year}-Q{(date.month - 1) // 3 + 1}"

    def get_prev(self, date: datetime.date) -> datetime.date:
        for i in [10, 7, 4]:
            if date.month > i:
                return datetime.date(date.year, i, 1)
        return datetime.date(date.year, 1, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        for i in [4, 7, 10]:
            if date.month < i:
                return datetime.date(date.year, i, 1)
        try:
            return datetime.date(date.year + 1, 1, 1)
        except ValueError:
            return datetime.date.max


class _IntervalMonth(Interval):
    """A month interval."""

    @property
    def label(self) -> str:
        return gettext("Monthly")

    def format_date(self, date: datetime.date) -> str:
        return date.strftime("%Y-%m")

    def get_prev(self, date: datetime.date) -> datetime.date:
        return datetime.date(date.year, date.month, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            month = (date.month % 12) + 1
            year = date.year + (date.month + 1 > 12)
            return datetime.date(year, month, 1)
        except ValueError:
            return datetime.date.max


class _IntervalWeek(Interval):
    """A week interval."""

    @property
    def label(self) -> str:
        return gettext("Weekly")

    def format_date(self, date: datetime.date) -> str:
        return date.strftime("%G-W%V")

    def get_prev(self, date: datetime.date) -> datetime.date:
        return date - timedelta(date.weekday())

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return date + timedelta(7 - date.weekday())
        except OverflowError:
            return datetime.date.max

    def number_of_days(self, date: datetime.date) -> int:  # noqa: ARG002
        """Get number of days in the surrounding interval."""
        return 7


class _IntervalDay(Interval):
    """A day interval."""

    @property
    def label(self) -> str:
        return gettext("Daily")

    def format_date(self, date: datetime.date) -> str:
        return date.strftime("%Y-%m-%d")

    def get_prev(self, date: datetime.date) -> datetime.date:
        return date

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return date + timedelta(1)
        except OverflowError:
            return datetime.date.max

    def number_of_days(self, date: datetime.date) -> int:  # noqa: ARG002
        return 1


Year = _IntervalYear()
Quarter = _IntervalQuarter()
Month = _IntervalMonth()
Week = _IntervalWeek()
Day = _IntervalDay()

INTERVALS = {
    "year": Year,
    "yearly": Year,
    "quarter": Quarter,
    "quarterly": Quarter,
    "month": Month,
    "monthly": Month,
    "week": Week,
    "weekly": Week,
    "day": Day,
    "daily": Day,
}


class InvalidDateRangeError(ValueError):
    """End date needs to be after begin date."""

    def __init__(self) -> None:
        super().__init__("End date needs to be after begin date.")


def interval_ends(
    begin: datetime.date,
    end: datetime.date,
    interval: Interval,
    *,
    complete: bool,
) -> Iterator[datetime.date]:
    """Get interval ends.

    Yields:
        The ends of the intervals.
    """
    if begin >= end:
        raise InvalidDateRangeError
    current = interval.get_prev(begin) if complete else begin
    while current < end:
        yield current
        current = interval.get_next(current)
    yield current if complete else end


ONE_DAY = timedelta(days=1)


@dataclass(frozen=True)
class DateRange:
    """A range of dates, usually matching an interval."""

    #: The inclusive start date of this range of dates.
    begin: datetime.date
    #: The exclusive end date of this range of dates.
    end: datetime.date

    def __post_init__(self) -> None:
        if self.begin >= self.end:
            raise InvalidDateRangeError

    @property
    def end_inclusive(self) -> datetime.date:
        """The last day of this interval."""
        return self.end - ONE_DAY


@listify
def dateranges(
    begin: datetime.date,
    end: datetime.date,
    interval: Interval,
    *,
    complete: bool,
) -> Iterable[DateRange]:
    """Get date ranges for the given begin and end date.

    Args:
        begin: The begin date - the first interval date range will
               include this date
        end: The end date - the last interval will end on or after
             date
        interval: The type of interval to generate ranges for.
        complete: Whether to complete starting and ending intervals.

    Yields:
        Date ranges for all intervals of the given in the
    """
    ends = interval_ends(begin, end, interval, complete=complete)
    left, right = tee(ends)
    next(right, None)
    for interval_begin, interval_end in zip(left, right, strict=False):
        yield DateRange(interval_begin, interval_end)


def local_today() -> datetime.date:
    """Today as a date in the local timezone."""
    return datetime.date.today()  # noqa: DTZ011


def substitute(
    string: str,
    fye: FiscalYearEnd | None = None,
) -> str:
    """Replace variables referring to the current day.

    Args:
        string: A string, possibly containing variables for today.
        fye: Use a specific fiscal-year-end

    Returns:
        A string, where variables referring to the current day, like 'year' or
        'week' have been replaced by the corresponding string understood by
        :func:`parse_date`.  Can compute addition and subtraction.
    """
    today = local_today()
    fye = fye or END_OF_YEAR

    for match in VARIABLE_RE.finditer(string):
        complete_match, interval, plusminus_, mod_ = match.group(0, 1, 2, 3)
        mod = int(mod_) if mod_ else 0
        offset = mod if plusminus_ == "+" else -mod
        if interval == "fiscal_year":
            after_fye = (today.month, today.day) > (fye.month_of_year, fye.day)
            year = today.year + (1 if after_fye else 0) - fye.year_offset
            string = string.replace(complete_match, f"FY{year + offset}")
        if interval == "year":
            string = string.replace(complete_match, str(today.year + offset))
        if interval == "fiscal_quarter":
            if not fye.has_quarters():
                raise FyeHasNoQuartersError
            target = month_offset(today.replace(day=1), offset * 3)
            after_fye = (target.month) > (fye.month_of_year)
            year = target.year + (1 if after_fye else 0) - fye.year_offset
            quarter = ((target.month - fye.month_of_year - 1) // 3) % 4 + 1
            string = string.replace(complete_match, f"FY{year}-Q{quarter}")
        if interval == "quarter":
            quarter_today = (today.month - 1) // 3 + 1
            year = today.year + (quarter_today + offset - 1) // 4
            quarter = (quarter_today + offset - 1) % 4 + 1
            string = string.replace(complete_match, f"{year}-Q{quarter}")
        if interval == "month":
            year = today.year + (today.month + offset - 1) // 12
            month = (today.month + offset - 1) % 12 + 1
            string = string.replace(complete_match, f"{year}-{month:02}")
        if interval == "week":
            string = string.replace(
                complete_match,
                (today + timedelta(offset * 7)).strftime("%G-W%V"),
            )
        if interval == "day":
            string = string.replace(
                complete_match,
                (today + timedelta(offset)).isoformat(),
            )
    return string


def parse_date(  # noqa: PLR0911
    string: str,
    fye: FiscalYearEnd | None = None,
) -> tuple[datetime.date | None, datetime.date | None]:
    """Parse a date.

    Example of supported formats:

    - 2010-03-15, 2010-03, 2010
    - 2010-W01, 2010-Q3
    - FY2012, FY2012-Q2

    Ranges of dates can be expressed in the following forms:

    - start - end
    - start to end

    where start and end look like one of the above examples

    Args:
        string: A date(range) in our custom format.
        fye: The fiscal year end to consider.

    Returns:
        A tuple (start, end) of dates.
    """
    string = string.strip().lower()
    if not string:
        return None, None

    string = substitute(string, fye).lower()

    match = IS_RANGE_RE.match(string)
    if match:
        return (
            parse_date(match.group(1), fye)[0],
            parse_date(match.group(2), fye)[1],
        )

    match = YEAR_RE.match(string)
    if match:
        year = int(match.group(0))
        start = datetime.date(year, 1, 1)
        return start, Year.get_next(start)

    match = MONTH_RE.match(string)
    if match:
        year, month = map(int, match.group(1, 2))
        start = datetime.date(year, month, 1)
        return start, Month.get_next(start)

    match = DAY_RE.match(string)
    if match:
        year, month, day = map(int, match.group(1, 2, 3))
        start = datetime.date(year, month, day)
        return start, Day.get_next(start)

    match = WEEK_RE.match(string)
    if match:
        year, week = map(int, match.group(1, 2))
        start = (
            datetime.datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%w")
            .replace(tzinfo=datetime.timezone.utc)
            .date()
        )
        return start, Week.get_next(start)

    match = QUARTER_RE.match(string)
    if match:
        year, quarter = map(int, match.group(1, 2))
        quarter_first_day = datetime.date(year, (quarter - 1) * 3 + 1, 1)
        return (
            quarter_first_day,
            Quarter.get_next(quarter_first_day),
        )

    match = FY_RE.match(string)
    if match:
        year = int(match.group(1))
        return get_fiscal_period(year, fye)

    match = FY_QUARTER_RE.match(string)
    if match:
        year, quarter = map(int, match.group(1, 2))
        return get_fiscal_period(year, fye, quarter)

    return None, None


def month_offset(date: datetime.date, months: int) -> datetime.date:
    """Offsets a date by a given number of months.

    Maintains the day, unless that day is invalid when it will
    raise a ValueError

    """
    year_delta, month = divmod(date.month - 1 + months, 12)

    return date.replace(year=date.year + year_delta, month=month + 1)


def parse_fye_string(fye: str) -> FiscalYearEnd | None:
    """Parse a string option for the fiscal year end.

    Args:
        fye: The end of the fiscal year to parse.
    """
    match = re.match(r"^(?P<month>\d{2})-(?P<day>\d{2})$", fye)
    if not match:
        return None
    month = int(match.group("month"))
    day = int(match.group("day"))
    try:
        _ = datetime.date(2001, (month - 1) % 12 + 1, day)
        return FiscalYearEnd(month, day)
    except ValueError:
        return None


def get_fiscal_period(
    year: int,
    fye: FiscalYearEnd | None,
    quarter: int | None = None,
) -> tuple[datetime.date | None, datetime.date | None]:
    """Calculate fiscal periods.

    Uses the fava option "fiscal-year-end" which should be in "%m-%d" format.
    Defaults to calendar year [12-31]

    Args:
        year: An integer year
        fye: End date for period in "%m-%d" format
        quarter: one of [None, 1, 2, 3 or 4]

    Returns:
        A tuple (start, end) of dates.

    """
    fye = fye or END_OF_YEAR
    start = (
        datetime.date(year - 1 + fye.year_offset, fye.month_of_year, fye.day)
        + ONE_DAY
    )
    # Special case 02-28 because of leap years
    if fye.month_of_year == 2 and fye.day == 28:
        start = start.replace(month=3, day=1)

    if quarter is None:
        return start, start.replace(year=start.year + 1)

    if not fye.has_quarters():
        return None, None

    if quarter < 1 or quarter > 4:
        return None, None

    start = month_offset(start, (quarter - 1) * 3)

    return start, month_offset(start, 3)


def days_in_daterange(
    start_date: datetime.date,
    end_date: datetime.date,
) -> Iterator[datetime.date]:
    """Yield a datetime for every day in the specified interval.

    Args:
        start_date: A start date.
        end_date: An end date (exclusive).

    Yields:
        All days between `start_date` to `end_date`.
    """
    for diff in range((end_date - start_date).days):
        yield start_date + timedelta(diff)
