import re
import datetime
import calendar
from dateutil.relativedelta import relativedelta


def get_next_interval(date, interval):
    if interval == 'year':
        return datetime.date(date.year + 1, 1, 1)
    elif interval == 'quarter':
        quarter = (date.month - 1) // 3 + 1
        month = quarter * 3 + 1
        year = date.year + (month > 12)
        return datetime.date(year, month % 12, 1)
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


months = [m.lower() for m in calendar.month_name]
months_abbr = [m.lower() for m in calendar.month_abbr]
all_months = months[1:] + months_abbr[1:]

rel_dates = {'yesterday': -1, 'today': 0, 'tomorrow': 1}
modifiers = {'this': 0, 'next': 1, 'last': -1}

is_range_re = re.compile('(.*?)\s(?:-|to)\s(.*)')

# this matches dates of the form 'year-month-day'
# day or month and day may be omitted
year_first_re = re.compile('^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$')

# this matches a week like 2016-W02 for the second week of 2016
week_re = re.compile('^(\d{4})-w(\d{2})$')

# this matches a quarter like 2016-Q1 for the first quarter of 2016
quarter_re = re.compile('^(\d{4})-q(\d)$')

# this will match any date of the form "day month_name year".
year_last_re = re.compile('^(?:{1} )?'
                          '({0})?(?: {1})?(?:,? )?'
                          '(\d{{4}})$'.
                          format('|'.join(all_months),
                                 '(?:(\d{1,2})(?:st|nd|rd|th)?)'))

# 'month_name modifier year' or 'modifier month/year/month_name'
mod_date_re = re.compile('(?:({}) )?({}) ({})'.format(
    '|'.join(all_months),
    '|'.join(list(modifiers.keys())),
    '|'.join(all_months + ['month', 'year'])))


def daterange(year=None, month=None, day=None, timedelta=datetime.timedelta()):
    """A helper function that returns a tuple with the starting and end date for
    the given range of dates. If called with empty arguments it will return
    the current day as start and beginning. Otherwise day or month and day may
    be omitted to get the whole month or whole year respectively. Timedelta is
    only used if all other arguments are none and if it is set the dates that
    will be returned are both 'today + timedelta'
    """
    year, month, day = map(lambda x: int(x) if x else None, (year, month, day))
    if not (year or month or day):
        start = datetime.date.today() + timedelta
        end = start + datetime.timedelta(days=1)
        return start, end
    elif (not year) or (day and not month):
        raise Exception
    elif (not day) and (not month):
        start = datetime.date(year, 1, 1)
        end = datetime.date(year + 1, 1, 1)
    elif (not day) and month:
        start = datetime.date(year, month, 1)
        end = datetime.date(year + (month > 11), (month % 12) + 1, 1)
    else:  # ~= if (year and month and day)
        start = datetime.date(year, month, day)
        end = start + datetime.timedelta(days=1)
    return start, end


def _parse_month(month):
    """Parse the given month name (either the full name or its abbreviation)
    to a number"""
    month = months.index(month) if month in months[1:] else month
    month = months_abbr.index(month) if month in months_abbr[1:] else month
    return month


def parse_date(string):
    """"Tries to parse the given string into two date objects marking the
    beginning and the end of the given period.

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
    if string.strip().lower() in ['year to date', 'ytd']:
        return parse_date(str(datetime.date.today().year) + ' - today')

    is_range = is_range_re.match(string)
    if is_range:
        return (parse_date(is_range.group(1))[0],
                parse_date(is_range.group(2))[1])
    string = string.strip().lower()
    if string == '':
        return None, None

    # check first if it is either yesterday, today or tomorrow
    if string in rel_dates:
        return daterange(timedelta=datetime.timedelta(days=rel_dates[string]))

    # try to match
    year_first = year_first_re.match(string)
    if year_first:
        year, month, day = year_first.group(1, 2, 3)
        return daterange(year, month, day)

    year_last = year_last_re.match(string)
    if year_last:
        month, year = year_last.group(2, 4)
        day = year_last.group(1) or year_last.group(3)
        return daterange(year, _parse_month(month), day)

    week = week_re.match(string)
    if week:
        year, week = week.group(1, 2)
        date_str = '{}{}1'.format(year, week)
        first_week_day = datetime.datetime.strptime(date_str, '%Y%W%w').date()
        return first_week_day, get_next_interval(first_week_day, 'week')

    quarter = quarter_re.match(string)
    if quarter:
        year, quarter = map(int, quarter.group(1, 2))
        quarter_first_day = datetime.date(year, (quarter - 1) * 3 + 1, 1)
        return quarter_first_day, get_next_interval(quarter_first_day,
                                                    'quarter')

    mod_date = mod_date_re.match(string)
    if mod_date:
        today = datetime.date.today()
        month, modifier, identifier = mod_date.group(1, 2, 3)
        modifier = modifiers[modifier]
        if identifier == 'year':
            month = _parse_month(month) if month else None
            return daterange(today.year + modifier, month)
        if identifier == 'month':
            m = today.replace(day=15) + modifier * datetime.timedelta(days=30)
            return daterange(m.year, m.month)
        else:
            return daterange(today.year + modifier, _parse_month(identifier))


def days_in_daterange(start_date, end_date):
    """Yields a datetime for every day in the specified interval."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + relativedelta(days=n)


def number_of_days_in_period(period, date_):
    """Returns the days in the specified period and date_."""

    if period == 'daily':
        return 1
    if period == 'weekly':
        return 7
    if period == 'monthly':
        date_ = datetime.datetime(date_.year, date_.month, 1)
        return ((date_ + relativedelta(months=1)) - date_).days
    if period == 'quarterly':
        quarter = (date_.month - 1) / 3 + 1
        if quarter == 1:
            date_ = datetime.datetime(date_.year, 1, 1)
        if quarter == 2:
            date_ = datetime.datetime(date_.year, 4, 1)
        if quarter == 3:
            date_ = datetime.datetime(date_.year, 7, 1)
        if quarter == 4:
            date_ = datetime.datetime(date_.year, 10, 1)
        return ((date_ + relativedelta(months=3)) - date_).days
    if period == 'yearly':
        date_ = datetime.datetime(date_.year, 1, 1)
        return ((date_ + relativedelta(years=1)) - date_).days
    raise Exception("Period unknown: {}".format(period))
