"""Date-related functionality.

Note:
    Date ranges are always tuples (start, end) from the (inclusive) start date
    to the (exclusive) end date.
"""

import enum
import re
import datetime

from flask_babel import gettext

IS_RANGE_RE = re.compile(r'(.*?)(?:-|to)(?=\s*\d{4})(.*)')

# these match dates of the form 'year-month-day'
# day or month and day may be omitted
YEAR_RE = re.compile(r'^\d{4}$')
MONTH_RE = re.compile(r'^(\d{4})-(\d{2})$')
DAY_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')

# this matches a week like 2016-W02 for the second week of 2016
WEEK_RE = re.compile(r'^(\d{4})-w(\d{2})$')

# this matches a quarter like 2016-Q1 for the first quarter of 2016
QUARTER_RE = re.compile(r'^(\d{4})-q(\d)$')

# this matches a financial year like FY2018 for the financial year ending 2018
FY_RE = re.compile(r'^fy(\d{4})$')

# this matches a quarter in a financial year like FY2018-Q2
FY_QUARTER_RE = re.compile(r'^fy(\d{4})-q(\d)$')

VARIABLE_RE = re.compile(r'\(?(fiscal_year|year|fiscal_quarter|quarter'
                         r'|month|week|day)(?:([-+])(\d+))?\)?')


class Interval(enum.Enum):
    """The possible intervals."""
    YEAR = 'year'
    QUARTER = 'quarter'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'

    @property
    def label(self):
        """The label for the interval."""
        return {
            Interval.YEAR: gettext('Yearly'),
            Interval.QUARTER: gettext('Quarterly'),
            Interval.MONTH: gettext('Monthly'),
            Interval.WEEK: gettext('Weekly'),
            Interval.DAY: gettext('Daily'),
        }.get(self)

    @staticmethod
    def get(string):
        """Return the enum member for a string."""
        try:
            return Interval[string.upper()]
        except KeyError:
            return Interval.MONTH

    @staticmethod
    def members():
        """Yield all members of this Enum."""
        for interval in Interval:
            yield interval


def get_next_interval(date: datetime.date, interval: Interval):
    """Get the start date of the next interval.

    Args:
        date: A date.
        interval: An interval.

    Returns:
        The start date of the next `interval` after `date`.

    """
    if interval is Interval.YEAR:
        return datetime.date(date.year + 1, 1, 1)
    if interval is Interval.QUARTER:
        for i in [4, 7, 10]:
            if date.month < i:
                return datetime.date(date.year, i, 1)
        return datetime.date(date.year + 1, 1, 1)
    if interval is Interval.MONTH:
        month = (date.month % 12) + 1
        year = date.year + (date.month + 1 > 12)
        return datetime.date(year, month, 1)
    if interval is Interval.WEEK:
        return date + datetime.timedelta(7 - date.weekday())
    if interval is Interval.DAY:
        return date + datetime.timedelta(1)
    raise NotImplementedError


def interval_ends(first, last, interval: Interval):
    """List intervals.

    Args:
        first: A datetime.date.
        last: A datetime.date.
        interval: An interval.

    Yields:
        Dates corresponding to the starts/ends of intervals between `first` and
        `last`.
    """
    while first < last:
        yield first
        first = get_next_interval(first, interval)

    yield last


def substitute(string, fye=None):    # pylint: disable=too-many-locals
    """Replace variables referring to the current day.

    Args:
        string: A string, possibly containing variables for today.
        fye: Use a specific fiscal-year-end

    Returns:
        A string, where variables referring to the current day, like 'year' or
        'week' have been replaced by the corresponding string understood by
        :func:`parse_date`.  Can compute addition and subtraction.
    """
    today = datetime.date.today()

    for match in VARIABLE_RE.finditer(string):
        complete_match, interval, plusminus, mod = match.group(0, 1, 2, 3)
        mod = int(mod) if mod else 0
        plusminus = 1 if plusminus == '+' else -1
        if interval == 'fiscal_year':
            year = today.year
            start, end = get_fiscal_period(year, fye=fye)
            if today >= end:
                year += 1
            year += plusminus * mod
            string = string.replace(complete_match, "FY{0}".format(year))
        if interval == 'year':
            year = today.year + plusminus * mod
            string = string.replace(complete_match, str(year))
        if interval == 'fiscal_quarter':
            target = month_offset(today.replace(day=1), plusminus * mod * 3)
            start, end = get_fiscal_period(target.year, fye=fye)
            if start.day != 1:
                raise ValueError("Cannot use fiscal_quarter if fiscal year "
                                 "does not start on first of the month")
            if target >= end:
                start = end
            quarter = int(((target.month - start.month) % 12) / 3)
            string = string.replace(complete_match, "FY{0}-Q{1}".format(
                start.year + 1, (quarter % 4) + 1))
        if interval == 'quarter':
            quarter_today = (today.month - 1) // 3 + 1
            year = today.year + (quarter_today + plusminus * mod - 1) // 4
            quarter = (quarter_today + plusminus * mod - 1) % 4 + 1
            string = string.replace(complete_match, '{}-Q{}'.format(
                year, quarter))
        if interval == 'month':
            year = today.year + (today.month + plusminus * mod - 1) // 12
            month = (today.month + plusminus * mod - 1) % 12 + 1
            string = string.replace(complete_match, '{}-{:02}'.format(
                year, month))
        if interval == 'week':
            delta = datetime.timedelta(plusminus * mod * 7)
            string = string.replace(complete_match,
                                    (today + delta).strftime('%Y-W%W'))
        if interval == 'day':
            delta = datetime.timedelta(plusminus * mod)
            string = string.replace(complete_match,
                                    (today + delta).isoformat())
    return string


def parse_date(string):  # pylint: disable=too-many-return-statements
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

    Returns:
        A tuple (start, end) of dates.

    """
    string = string.strip().lower()
    if not string:
        return None, None

    string = substitute(string).lower()

    match = IS_RANGE_RE.match(string)
    if match:
        return (parse_date(match.group(1))[0], parse_date(match.group(2))[1])

    match = YEAR_RE.match(string)
    if match:
        year = int(match.group(0))
        start = datetime.date(year, 1, 1)
        return start, get_next_interval(start, Interval.YEAR)

    match = MONTH_RE.match(string)
    if match:
        year, month = map(int, match.group(1, 2))
        start = datetime.date(year, month, 1)
        return start, get_next_interval(start, Interval.MONTH)

    match = DAY_RE.match(string)
    if match:
        year, month, day = map(int, match.group(1, 2, 3))
        start = datetime.date(year, month, day)
        return start, get_next_interval(start, Interval.DAY)

    match = WEEK_RE.match(string)
    if match:
        year, week = match.group(1, 2)
        date_str = '{}{}1'.format(year, week)
        first_week_day = datetime.datetime.strptime(date_str, '%Y%W%w').date()
        return first_week_day, get_next_interval(first_week_day,
                                                 Interval.WEEK)

    match = QUARTER_RE.match(string)
    if match:
        year, quarter = map(int, match.group(1, 2))
        quarter_first_day = datetime.date(year, (quarter - 1) * 3 + 1, 1)
        return quarter_first_day, get_next_interval(quarter_first_day,
                                                    Interval.QUARTER)

    match = FY_RE.match(string)
    if match:
        year = int(match.group(1))
        return get_fiscal_period(year)

    match = FY_QUARTER_RE.match(string)
    if match:
        year, quarter = map(int, match.group(1, 2))
        return get_fiscal_period(year, quarter)

    return None, None


def month_offset(date, months):
    """Offsets a date by a given number of months

    Maintains the day, unless that day is invalid when it will
    raise a ValueError

    """

    year_delta, month = divmod(date.month - 1 + months, 12)

    return date.replace(year=date.year + year_delta, month=month + 1)


def get_fiscal_period(year, quarter=None, fye=None):
    """Calculates fiscal periods

    Uses the fava option "fiscal-year-end" which should be in "%m-%d" format.
    Defaults to calendar year [12-31]

    Args:
        year: An interger year
        quarter: one of [None, 1, 2, 3 or 4]
        fye: End date for period in "%m-%d" format

    Returns:
        A tuple (start, end) of dates.

    """
    if fye is None:
        from flask import g
        fye = g.ledger.fava_options['fiscal-year-end']

    try:
        start_date = (datetime.datetime.strptime('{0}-{1}'.format(
            year - 1, fye), '%Y-%m-%d') + datetime.timedelta(days=1)).date()
    except ValueError:
        return None, None

    if quarter is None:
        return start_date, start_date.replace(year=start_date.year + 1)

    if start_date.day != 1:
        # quarters make no sense in jurisdictions where period starts
        # on a date (UK etc)
        return None, None

    if quarter < 1 or quarter > 4:
        return None, None

    if quarter > 1:
        start_date = month_offset(start_date, (quarter - 1) * 3)

    end_date = month_offset(start_date, 3)
    return start_date, end_date


def days_in_daterange(start_date, end_date):
    """Yield a datetime for every day in the specified interval.

    Args:
        start_date: A start date.
        end_date: An end date (exclusive).

    Returns:
        An iterator yielding all days between `start_date` to `end_date`.

    """
    for diff in range((end_date - start_date).days):
        yield start_date + datetime.timedelta(diff)


def number_of_days_in_period(interval, date):
    """Number of days in the surrounding interval.

    Args:
        interval: An interval.
        date: A date.

    Returns:
        A number, the number of days surrounding the given date in the
        interval.
    """

    if interval is Interval.DAY:
        return 1
    if interval is Interval.WEEK:
        return 7
    if interval is Interval.MONTH:
        date = datetime.date(date.year, date.month, 1)
        return (get_next_interval(date, Interval.MONTH) - date).days
    if interval is Interval.QUARTER:
        quarter = (date.month - 1) / 3 + 1
        date = datetime.date(date.year, int(quarter) * 3 - 2, 1)
        return (get_next_interval(date, Interval.QUARTER) - date).days
    if interval is Interval.YEAR:
        date = datetime.date(date.year, 1, 1)
        return (get_next_interval(date, Interval.YEAR) - date).days
    raise NotImplementedError
