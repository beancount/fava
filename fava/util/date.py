import re
import datetime
import calendar


months = [m.lower() for m in calendar.month_name]
months_abbr = [m.lower() for m in calendar.month_abbr]
all_months = months[1:] + months_abbr[1:]

rel_dates = {'yesterday': -1, 'today': 0, 'tomorrow': 1}
modifiers = {'this': 0, 'next': 1, 'last': -1}

is_range_re = re.compile(r'(.*?)\s(?:-|to)\s(.*)')

# this matches dates of the form 'year-month-day'
# day or month and day may be omitted
year_first_re = re.compile(r'^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$')

# this matches a week like 2016-W02 for the second week of 2016
week_re = re.compile(r'^(\d{4})-w(\d{2})$')

# this matches a quarter like 2016-Q1 for the first quarter of 2016
quarter_re = re.compile(r'^(\d{4})-q(\d)$')

# this will match any date of the form "day month_name year".
year_last_re = re.compile(r'^(?:{1} )?'
                          r'({0})?(?: {1})?(?:,? )?'
                          r'(\d{{4}})$'.
                          format('|'.join(all_months),
                                 r'(?:(\d{1,2})(?:st|nd|rd|th)?)'))

# 'month_name modifier year' or 'modifier month/year/month_name'
mod_date_re = re.compile('(?:({}) )?({}) ({})'.format(
    '|'.join(all_months),
    '|'.join(list(modifiers.keys())),
    '|'.join(all_months + ['month', 'year'])))

rel_date_re = re.compile(
    # d, day
    # w, week
    # m, month
    # q, quarter
    # y, year
    r'(d|day|w|week|m|month|q|quarter|y|year)([+-]\d+)'
)


def get_interval(date, interval, is_next):
    """Get the closest interval based on given date.

    Intervals are defined as (relative to given date):
        - day: today/tomorrow
        - week: previous/next Monday
        - quarter: the first day of current/next quarter
        - month: the first day of current/next month
        - year: the first day of curren/next year
    """
    if interval == 'year':
        return datetime.date(date.year + is_next, 1, 1)
    elif interval == 'quarter':
        if is_next:
            for i in [4, 7, 10]:
                if date.month < i:
                    return datetime.date(date.year, i, 1)
            return datetime.date(date.year + 1, 1, 1)
        else:
            for i in [10, 7, 4, 1]:
                if date.month >= i:
                    return datetime.date(date.year, i, 1)
    elif interval == 'month':
        if is_next:
            month = date.month % 12 + 1
            year = date.year + (month < date.month)
            return datetime.date(year, month, 1)
        else:
            return date.replace(day=1)
    elif interval == 'week':
        return date + datetime.timedelta(7 * is_next - date.weekday())
    elif interval == 'day':
        return date + datetime.timedelta(1) * is_next
    else:
        raise NotImplementedError


def get_next_interval(date, interval):
    return get_interval(date, interval, is_next=True)


def get_previous_interval(date, interval):
    return get_interval(date, interval, is_next=False)


def interval_tuples(first, last, interval):
    if not first:
        return []

    intervals = []
    while first < last:
        next_date = get_next_interval(first, interval)
        intervals.append((first, next_date))
        first = next_date

    return intervals


def daterange(year=None, month=None, day=None):
    """A helper function that returns a tuple with the starting and end date for
    the given range of dates. Day or month and day may be omitted to get the
    whole month or whole year respectively."""
    year, month, day = (int(x) if x else None for x in (year, month, day))
    if (not day) and (not month):
        start = datetime.date(year, 1, 1)
        return start, get_next_interval(start, 'year')
    if (not day) and month:
        start = datetime.date(year, month, 1)
        return start, get_next_interval(start, 'month')
    if year and month and day:
        start = datetime.date(year, month, day)
        return start, get_next_interval(start, 'day')


def _parse_month(month):
    """Parse the given month name (either the full name or its abbreviation)
    to a number"""
    if month in months[1:]:
        return months.index(month)
    if month in months_abbr[1:]:
        return months_abbr.index(month)


def parse_date(string):
    """"Tries to parse the given string into two date objects marking the
    beginning and the end of the given period, where the end day is exclusive,
    i.e. one day after the end of the period.

    Example of supported formats:
     - today, tomorrow, yesterday
     - 2010-03-15, 2010-03, 2010
     - march 2010, mar 2010
     - this month, last year, next year
     - october this year, aug last year
     - year to date, ytd

    Ranges of dates can be expressed in the following forms:
     - start - end
     - start to end
    where start and end look like one of the above examples
    """
    string = string.strip().lower()
    if not string:
        return None, None

    today = datetime.date.today()

    if string in ['year to date', 'ytd']:
        return datetime.date(today.year, 1, 1), get_next_interval(today, 'day')

    match = is_range_re.match(string)
    if match:
        return (parse_date(match.group(1))[0],
                parse_date(match.group(2))[1])

    # check if it is either yesterday, today or tomorrow
    if string in rel_dates:
        start = today + datetime.timedelta(rel_dates[string])
        return start, get_next_interval(start, 'day')

    match = year_first_re.match(string)
    if match:
        year, month, day = match.group(1, 2, 3)
        return daterange(year, month, day)

    match = year_last_re.match(string)
    if match:
        month, year = match.group(2, 4)
        day = match.group(1) or match.group(3)
        return daterange(year, _parse_month(month), day)

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

    match = mod_date_re.match(string)
    if match:
        month, modifier, identifier = match.group(1, 2, 3)
        modifier = modifiers[modifier]
        if identifier == 'year':
            month = _parse_month(month) if month else None
            return daterange(today.year + modifier, month)
        if identifier == 'month':
            m = today.replace(day=15) + modifier * datetime.timedelta(days=30)
            return daterange(m.year, m.month)
        else:
            return daterange(today.year + modifier, _parse_month(identifier))

    match = rel_date_re.match(string)
    if match:
        unit, number = match.group(1, 2)
        number = int(number)
        unit = unit[:1]
        return _relative_date(today, number, unit)


def _relative_date(today, number, unit):
    if unit == 'd':
        date = today + datetime.timedelta(days=1) * number
        return (get_previous_interval(date, 'day'),
                get_next_interval(date, 'day'))
    elif unit == 'w':
        date = today + datetime.timedelta(days=7) * number
        return (get_previous_interval(date, 'week'),
                get_next_interval(date, 'week'))
    elif unit == 'q':
        delta_months = 3 * number
        year_delta, result_month = divmod(today.month + delta_months, 12)
        if result_month == 0:
            result_month = 12
            year_delta -= 1
        date = today.replace(year=today.year + year_delta,
                             month=result_month,
                             day=1)
        return (get_previous_interval(date, 'quarter'),
                get_next_interval(date, 'quarter'))
    elif unit == 'm':
        year_delta, result_month = divmod(today.month + number, 12)
        if result_month == 0:
            result_month = 12
            year_delta -= 1
        date = today.replace(year=today.year + year_delta,
                             month=result_month,
                             day=1)
        return (get_previous_interval(date, 'month'),
                get_next_interval(date, 'month'))
    elif unit == 'y':
        date = today.replace(year=today.year + number)
        return (get_previous_interval(date, 'year'),
                get_next_interval(date, 'year'))


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
