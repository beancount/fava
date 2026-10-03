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
from itertools import pairwise
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

ONE_DAY = timedelta(1)


class FiscalYearEnd:
    """Month and day that specify the end of the fiscal year."""

    __slots__ = (
        "day",
        "month",
        "month_of_year",
        "start_day",
        "start_month_of_year",
        "year_offset",
    )

    month: int
    """Month of the fiscal year end - can be between 1 and 24."""
    day: int
    """Day of the fiscal year end."""
    month_of_year: int
    """Actual month of the year."""
    year_offset: int
    """Number of years that this is offset into the future."""

    def __init__(self, month: int, day: int) -> None:
        if month < 1 or month > 24:
            msg = f"Invalid fiscal year end month: {month}"
            raise ValueError(msg)
        self.month = month
        self.day = day
        self.month_of_year = (self.month - 1) % 12 + 1
        self.year_offset = (self.month - 1) // 12
        start = datetime.date(2001, self.month_of_year, self.day) + ONE_DAY
        self.start_month_of_year = start.month
        self.start_day = start.day

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FiscalYearEnd)
            and self.day == other.day
            and self.month == other.month
        )

    def __hash__(self) -> int:
        return hash((self.month, self.day))

    def __repr__(self) -> str:
        return f"FiscalYearEnd(month={self.month}, day={self.day})"

    def fiscal_year(self, date: datetime.date) -> int:
        """The fiscal year that a date is in."""
        after_start = (date.month, date.day) >= (
            self.start_month_of_year,
            self.start_day,
        )
        wraps = self.start_month_of_year < self.month_of_year
        return date.year + (after_start and not wraps) - self.year_offset

    def begin_date_for_year(self, year: int) -> datetime.date:
        """Calculate the begin date of a fiscal year."""
        wraps = self.start_month_of_year < self.month_of_year
        return datetime.date(
            year - 1 + wraps + self.year_offset,
            self.start_month_of_year,
            self.start_day,
        )


class FyeHasNoQuartersError(ValueError):
    """Only fiscal years that start on the first of a month have quarters."""

    def __init__(self) -> None:
        super().__init__(self.__doc__)


END_OF_YEAR = FiscalYearEnd(12, 31)
"""Default fiscal year (12-31)."""


class FiscalYearEnds:
    """Some common fiscal year ends, used in tests."""

    AU_NZ = FiscalYearEnd(6, 30)
    """Fiscal year for Australia / New Zealand (06-30)."""
    JP = FiscalYearEnd(15, 31)
    """Fiscal year for Japan (15-31)."""
    UK = FiscalYearEnd(4, 5)
    """Fiscal year for the UK (04-05)."""
    US = FiscalYearEnd(9, 30)
    """Fiscal year for the US (09-30)."""
    ZA = FiscalYearEnd(2, 28)
    """Fiscal year for the personal tax year in South Africa (02-28)."""


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
        return f"{date.year:04d}"

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
        return f"{date.year:04d}-Q{(date.month - 1) // 3 + 1}"

    def get_prev(self, date: datetime.date) -> datetime.date:
        return datetime.date(date.year, (date.month - 1) // 3 * 3 + 1, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        year_delta, month0 = divmod((date.month - 1) // 3 * 3 + 3, 12)
        try:
            return datetime.date(date.year + year_delta, month0 + 1, 1)
        except ValueError:
            return datetime.date.max


class _IntervalMonth(Interval):
    """A month interval."""

    @property
    def label(self) -> str:
        return gettext("Monthly")

    def format_date(self, date: datetime.date) -> str:
        return f"{date.year:04d}-{date.month:02d}"

    def get_prev(self, date: datetime.date) -> datetime.date:
        return datetime.date(date.year, date.month, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        year_delta, month0 = divmod(date.month, 12)
        try:
            return datetime.date(date.year + year_delta, month0 + 1, 1)
        except ValueError:
            return datetime.date.max


class _IntervalWeek(Interval):
    """A week interval."""

    @property
    def label(self) -> str:
        return gettext("Weekly")

    def format_date(self, date: datetime.date) -> str:
        iso = date.isocalendar()
        return f"{iso.year:04d}-W{iso.week:02d}"

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


class _IntervalFortnight(Interval):
    """A fortnight interval: fixed 14-day blocks starting on a Monday.

    The blocks are counted from a fixed Monday, so they never overlap and
    never shrink to one week in a 53-week year, which pairs of ISO weeks
    would. Only budgets use this interval; it is not a report interval.
    """

    _epoch = datetime.date(1970, 1, 5)  # a Monday

    @property
    def label(self) -> str:
        return gettext("Fortnightly")

    def format_date(self, date: datetime.date) -> str:
        return self.get_prev(date).strftime("%Y-%m-%d")

    def get_prev(self, date: datetime.date) -> datetime.date:
        return date - timedelta((date - self._epoch).days % 14)

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return self.get_prev(date) + timedelta(14)
        except OverflowError:
            return datetime.date.max

    @override
    def number_of_days(self, date: datetime.date) -> int:
        return 14


class _IntervalDay(Interval):
    """A day interval."""

    @property
    def label(self) -> str:
        return gettext("Daily")

    def format_date(self, date: datetime.date) -> str:
        return date.isoformat()

    def get_prev(self, date: datetime.date) -> datetime.date:
        return date

    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return date + ONE_DAY
        except OverflowError:
            return datetime.date.max

    @override
    def number_of_days(self, date: datetime.date) -> int:
        return 1


@dataclass(frozen=True, slots=True)
class FiscalYear(Interval):
    """A fiscal year interval, for a specific fiscal year end."""

    fye: FiscalYearEnd

    @property
    @override
    def label(self) -> str:
        return gettext("Per Fiscal Year")

    @override
    def format_date(self, date: datetime.date) -> str:
        return f"FY{self.fye.fiscal_year(date):04d}"

    @override
    def get_prev(self, date: datetime.date) -> datetime.date:
        start = date.replace(
            month=self.fye.start_month_of_year, day=self.fye.start_day
        )
        return start.replace(year=date.year - 1) if date < start else start

    @override
    def get_next(self, date: datetime.date) -> datetime.date:
        start = date.replace(
            month=self.fye.start_month_of_year, day=self.fye.start_day
        )
        try:
            return start if date < start else start.replace(year=date.year + 1)
        except ValueError:
            return datetime.date.max


@dataclass(frozen=True, slots=True)
class FiscalQuarter(Interval):
    """A fiscal quarter interval, for a specific fiscal year end."""

    fye: FiscalYearEnd

    def __post_init__(self) -> None:
        if self.fye.start_day != 1:
            raise FyeHasNoQuartersError

    @property
    @override
    def label(self) -> str:
        return gettext("Per Fiscal Quarter")

    @override
    def format_date(self, date: datetime.date) -> str:
        quarter = ((date.month - self.fye.start_month_of_year) % 12) // 3
        return f"FY{self.fye.fiscal_year(date):04d}-Q{quarter + 1}"

    @override
    def get_prev(self, date: datetime.date) -> datetime.date:
        month_in_quarter = (date.month - self.fye.start_month_of_year) % 3
        return month_offset(date.replace(day=1), -month_in_quarter)

    @override
    def get_next(self, date: datetime.date) -> datetime.date:
        try:
            return month_offset(self.get_prev(date), 3)
        except ValueError:
            return datetime.date.max


Year = _IntervalYear()
Quarter = _IntervalQuarter()
Month = _IntervalMonth()
Week = _IntervalWeek()
Fortnight = _IntervalFortnight()
Day = _IntervalDay()


_INTERVALS = {
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

#: Intervals that only a budget directive can use.
_BUDGET_ONLY_INTERVALS = {
    "fortnight": Fortnight,
    "fortnightly": Fortnight,
}


def get_interval(value: str, fye: FiscalYearEnd) -> Interval | None:
    """Get the interval for a string name."""
    lowered = value.lower()
    interval = _INTERVALS.get(lowered)
    if interval is not None:
        return interval
    if fye == END_OF_YEAR:
        return None
    if lowered == "fiscal_year":
        return FiscalYear(fye)
    if lowered == "fiscal_quarter":
        try:
            return FiscalQuarter(fye)
        except FyeHasNoQuartersError:
            return None
    return None


def get_budget_interval(value: str, fye: FiscalYearEnd) -> Interval | None:
    """Get the interval for a budget directive's period name."""
    return _BUDGET_ONLY_INTERVALS.get(value.lower()) or get_interval(
        value, fye
    )


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


@dataclass(frozen=True, slots=True)
class DateRange:
    """A range of dates, usually matching an interval."""

    begin: datetime.date
    """The inclusive start date of this range of dates."""
    end: datetime.date
    """The exclusive end date of this range of dates."""

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
        Date ranges for all intervals between begin and end date.
    """
    ends = interval_ends(begin, end, interval, complete=complete)
    for interval_begin, interval_end in pairwise(ends):
        yield DateRange(interval_begin, interval_end)


def local_today() -> datetime.date:
    """Today as a date in the local timezone."""
    return datetime.date.today()  # noqa: DTZ011


def month_offset(date: datetime.date, months: int) -> datetime.date:
    """Offsets a date by a given number of months."""
    year_delta, month0 = divmod(date.month - 1 + months, 12)
    return date.replace(year=date.year + year_delta, month=month0 + 1)


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
        return FiscalYearEnd(month, day)
    except ValueError:
        return None


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
