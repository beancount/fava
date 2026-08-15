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
        return datetime.date(date.year, (date.month - 1) // 3 * 3 + 1, 1)

    def get_next(self, date: datetime.date) -> datetime.date:
        month = (date.month - 1) // 3 * 3 + 4
        try:
            return datetime.date(date.year + (month > 12), month % 12, 1)
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
