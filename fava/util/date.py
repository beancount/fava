import re
import datetime

is_range_re = re.compile(r'(.*?)(?:-|to)(?=\s*\d{4})(.*)')

# these match dates of the form 'year-month-day'
# day or month and day may be omitted
year_re = re.compile(r'^\d{4}$')
month_re = re.compile(r'^(\d{4})-(\d{2})$')
day_re = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')

# this matches a week like 2016-W02 for the second week of 2016
week_re = re.compile(r'^(\d{4})-w(\d{2})$')

# this matches a quarter like 2016-Q1 for the first quarter of 2016
quarter_re = re.compile(r'^(\d{4})-q(\d)$')


def get_next_interval(date, interval):
    if interval == 'year':
        return datetime.date(date.year + 1, 1, 1)
    elif interval == 'quarter':
        for i in [4, 7, 10]:
            if date.month < i:
                return datetime.date(date.year, i, 1)
        return datetime.date(date.year + 1, 1, 1)
    elif interval == 'month':
        month = (date.month % 12) + 1
        year = date.year + (date.month + 1 > 12)
        return datetime.date(year, month, 1)
    elif interval == 'week':
        return date + datetime.timedelta(7 - date.weekday())
    elif interval == 'day':
        return date + datetime.timedelta(1)
    else:
        raise NotImplementedError


def interval_tuples(first, last, interval):
    if not first:
        return []

    intervals = []
    while first < last:
        next_date = get_next_interval(first, interval)
        intervals.append((first, next_date))
        first = next_date

    return intervals


def parse_date(string):
    """"Tries to parse the given string into two date objects marking the
    beginning and the end of the given period, where the end day is exclusive,
    i.e. one day after the end of the period.

    Example of supported formats:
     - 2010-03-15, 2010-03, 2010
     - 2010-W01, 2010-Q3

    Ranges of dates can be expressed in the following forms:
     - start - end
     - start to end
    where start and end look like one of the above examples
    """
    string = string.strip().lower()
    if not string:
        return None, None

    match = is_range_re.match(string)
    if match:
        return (parse_date(match.group(1))[0],
                parse_date(match.group(2))[1])

    match = year_re.match(string)
    if match:
        year = int(match.group(0))
        start = datetime.date(year, 1, 1)
        return start, get_next_interval(start, 'year')

    match = month_re.match(string)
    if match:
        year, month = map(int, match.group(1, 2))
        start = datetime.date(year, month, 1)
        return start, get_next_interval(start, 'month')

    match = day_re.match(string)
    if match:
        year, month, day = map(int, match.group(1, 2, 3))
        start = datetime.date(year, month, day)
        return start, get_next_interval(start, 'day')

    match = week_re.match(string)
    if match:
        year, week = match.group(1, 2)
        date_str = '{}{}1'.format(year, week)
        first_week_day = datetime.datetime.strptime(date_str, '%Y%W%w').date()
        return first_week_day, get_next_interval(first_week_day, 'week')

    match = quarter_re.match(string)
    if match:
        year, quarter = map(int, match.group(1, 2))
        quarter_first_day = datetime.date(year, (quarter - 1) * 3 + 1, 1)
        return quarter_first_day, get_next_interval(quarter_first_day,
                                                    'quarter')


def days_in_daterange(start_date, end_date):
    """Yields a datetime for every day in the specified interval, excluding
    end_date."""
    for diff in range((end_date - start_date).days):
        yield start_date + datetime.timedelta(diff)


def number_of_days_in_period(period, date_):
    """Returns the days in the specified period and date_."""

    if period == 'daily':
        return 1
    if period == 'weekly':
        return 7
    if period == 'monthly':
        date_ = datetime.date(date_.year, date_.month, 1)
        return (get_next_interval(date_, 'month') - date_).days
    if period == 'quarterly':
        quarter = (date_.month - 1) / 3 + 1
        date_ = datetime.date(date_.year, int(quarter) * 3 - 2, 1)
        return (get_next_interval(date_, 'quarter') - date_).days
    if period == 'yearly':
        date_ = datetime.date(date_.year, 1, 1)
        return (get_next_interval(date_, 'year') - date_).days
    raise Exception("Period unknown: {}".format(period))
