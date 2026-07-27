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

try:
    from typing import override
except ImportError:  # pragma: no cover
    from typing_extensions import override

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

# Elasticsearch/Grafana date-math: now[+/-Nunit][/snap]
# Units: y, M, w, d (date-only, no h/m/s for beancount)
# Snaps: y, M, w, d, fy, fQ
DATEMATH_RE = re.compile(
    r"now"
    r"(?:\s*([+-])\s*(\d+)\s*([yMwWd]))?"
    r"(?:\s*/\s*(fy|fq|[yMwWd]))?",
    re.IGNORECASE,
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

    @override
    def number_of_days(self, date: datetime.date) -> int:
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

    @override
    def number_of_days(self, date: datetime.date) -> int:
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


def _snap_date(
    date: datetime.date,
    snap: str,
    fye: FiscalYearEnd,
) -> datetime.date:
    """Snap a date to the start of the given period.

    Supports: y, M, w, d, fy (fiscal year), fQ (fiscal quarter).
    """
    snap_lower = snap.lower()
    if snap_lower == "d":
        return date
    if snap_lower == "w":
        return date - timedelta(date.weekday())
    if snap_lower == "m":
        return datetime.date(date.year, date.month, 1)
    if snap_lower == "y":
        return datetime.date(date.year, 1, 1)
    if snap_lower == "fy":
        after_fye = (date.month, date.day) > (fye.month_of_year, fye.day)
        year = date.year + (1 if after_fye else 0) - fye.year_offset
        start, _ = get_fiscal_period(year, fye)
        return start if start is not None else datetime.date.min
    if snap_lower == "fq":
        if not fye.has_quarters():
            raise FyeHasNoQuartersError
        after_fye = (date.month, date.day) > (fye.month_of_year, fye.day)
        year = date.year + (1 if after_fye else 0) - fye.year_offset
        # find which fiscal quarter the date falls into
        start_year, _ = get_fiscal_period(year, fye)
        if start_year is None:
            return datetime.date.min
        # how many months since fiscal year start
        months_since = (date.year - start_year.year) * 12 + date.month - start_year.month
        quarter = max(1, min(4, months_since // 3 + 1))
        start, _ = get_fiscal_period(year, fye, quarter)
        return start if start is not None else datetime.date.min
    msg = f"Unknown date math snap: {snap}"
    raise ValueError(msg)


def _period_end_from_snap(date: datetime.date, snap: str, fye: FiscalYearEnd) -> datetime.date:
    """Given a snapped start date, return the (exclusive) end date."""
    snap_lower = snap.lower()
    if snap_lower == "d":
        return Day.get_next(date)
    if snap_lower == "w":
        return Week.get_next(date)
    if snap_lower == "m":
        return Month.get_next(date)
    if snap_lower == "y":
        return Year.get_next(date)
    if snap_lower == "fy":
        # determine the fiscal year label for this start date
        after_fye = (date.month, date.day) > (fye.month_of_year, fye.day)
        year = date.year + (1 if after_fye else 0) - fye.year_offset
        _, end = get_fiscal_period(year, fye)
        return end if end is not None else datetime.date.max
    if snap_lower == "fq":
        # determine fiscal year/quarter for this start date
        after_fye = (date.month, date.day) > (fye.month_of_year, fye.day)
        year = date.year + (1 if after_fye else 0) - fye.year_offset
        if not fye.has_quarters():
            raise FyeHasNoQuartersError
        start_year, _ = get_fiscal_period(year, fye)
        if start_year is None:
            return datetime.date.max
        months_since = (date.year - start_year.year) * 12 + date.month - start_year.month
        quarter = max(1, min(4, months_since // 3 + 1))
        _, end = get_fiscal_period(year, fye, quarter)
        return end if end is not None else datetime.date.max
    msg = f"Unknown date math snap: {snap}"
    raise ValueError(msg)


def _unit_from_match(match: re.Match[str]) -> str:
    """Extract the unit from a DATEMATH_RE match, defaulting to 'd'."""
    return match.group(3) or "d"


def _eval_datemath(
    string: str,
    fye: FiscalYearEnd,
) -> datetime.date | None:
    """Evaluate a single date-math expression like 'now-1y' or 'now/M'.

    Returns the (possibly snapped) anchor date, or None if the string is
    not date math.  Without an explicit snap, the offset is applied as a
    simple shift (no period snapping).  With a snap (/d, /M, /y, /fy, /fQ),
    the result is rounded down to the start of that period.
    """
    match = DATEMATH_RE.match(string.strip())
    if not match:
        return None
    today = local_today()
    plusminus, amount_str, unit, snap = match.group(1, 2, 3, 4)
    date = today
    if amount_str:
        amount = int(amount_str)
        unit_lower = (unit or "d").lower()
        delta: int = amount if plusminus == "+" else -amount
        if unit_lower == "d":
            date += timedelta(days=delta)
        elif unit_lower == "w":
            date += timedelta(weeks=delta)
        elif unit_lower == "m":
            date = month_offset(date.replace(day=1), delta)
        elif unit_lower == "y":
            try:
                date = date.replace(year=date.year + delta)
            except ValueError:
                return None  # pragma: no cover
    if snap:
        return _snap_date(date, snap, fye)
    return date


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


# Date-math range: "now-30d - now", "now/M - now/d", etc.
DATEMATH_RANGE_RE = re.compile(
    r"(now\S*)\s*(?:-|to)\s*(now\S*)",
    re.IGNORECASE,
)


def _parse_datemath(
    string: str,
    fye: FiscalYearEnd,
) -> tuple[datetime.date | None, datetime.date | None]:
    """Try to parse a date-math expression (now-1y, now/M, etc.).

    Returns (begin, end) or (None, None) if not a date-math expression.
    """
    s = string.strip().lower()
    if not s.startswith("now"):
        return None, None

    # Check for range: now-30d - now, now/M - now/d, etc.
    range_match = DATEMATH_RANGE_RE.match(s)
    if range_match:
        start = _eval_datemath(range_match.group(1), fye)
        end = _eval_datemath(range_match.group(2), fye)
        if start is not None and end is not None:
            return start, end
        return None, None

    # Single date-math expression
    start = _eval_datemath(s, fye)
    if start is None:
        return None, None

    # Determine end from the snap or unit.
    # Without an explicit snap, the unit determines both the snap and the
    # period length, e.g. now-1M means "the calendar month one month ago".
    match = DATEMATH_RE.match(s)
    if match:
        snap = match.group(4)
        period = snap or _unit_from_match(match) or "d"
        start = _snap_date(start, period, fye)
        end = _period_end_from_snap(start, period, fye)
        return start, end

    return start, Day.get_next(start)


def parse_date(  # noqa: PLR0911
    string: str,
    fye: FiscalYearEnd | None = None,
) -> tuple[datetime.date | None, datetime.date | None]:
    """Parse a date.

    Example of supported formats:

    - 2010-03-15, 2010-03, 2010
    - 2010-W01, 2010-Q3
    - FY2012, FY2012-Q2
    - now, now-1y, now/M, now-1y/y, now-1M - now

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

    fye = fye or END_OF_YEAR

    # Try date-math first (now-1y, now/M, etc.)
    datemath_result = _parse_datemath(string, fye)
    if datemath_result != (None, None):
        return datemath_result

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


def parse_date_resolved(
    string: str,
    fye: FiscalYearEnd | None = None,
) -> tuple[datetime.date | None, datetime.date | None, str]:
    """Like parse_date but also returns a human-readable description.

    Returns:
        A tuple (start, end, description) where description is something
        like "2024-01-01 to 2024-12-31" showing the resolved range.
    """
    begin, end = parse_date(string, fye)
    if begin is None or end is None:
        return None, None, ""
    return begin, end, f"{begin.isoformat()} to {(end - ONE_DAY).isoformat()}"


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
