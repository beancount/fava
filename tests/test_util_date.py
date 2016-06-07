from datetime import date
from datetime import datetime as dt

import pytest

from fava.util.date import (_parse_month, parse_date, daterange,
                            get_next_interval, interval_tuples,
                            number_of_days_in_period)


@pytest.mark.parametrize('input_date_string,interval,expect', [
    ('2016-01-01', 'day', '2016-01-02'),
    ('2016-01-01', 'week', '2016-01-04'),
    ('2016-01-01', 'month', '2016-02-01'),
    ('2016-01-01', 'quarter', '2016-04-01'),
    ('2016-01-01', 'year', '2017-01-01'),

    ('2016-12-31', 'day', '2017-01-01'),
    ('2016-12-31', 'week', '2017-01-02'),
    ('2016-12-31', 'month', '2017-01-01'),
    ('2016-12-31', 'quarter', '2017-01-01'),
    ('2016-12-31', 'year', '2017-01-01'),
])
def test_get_next_interval(input_date_string, interval, expect):
    """Test for get_next_interval function."""
    input_date = dt.strptime(input_date_string, '%Y-%m-%d')
    get = get_next_interval(input_date, interval)
    assert get.strftime('%Y-%m-%d') == expect


def test_get_next_interval_exception():
    with pytest.raises(NotImplementedError):
        get_next_interval(date(2016, 4, 18), 'decade')


def test_interval_tuples():
    assert interval_tuples(date(2014, 3, 5), date(2014, 5, 5), 'month') == [
        (date(2014, 3, 5), date(2014, 4, 1)),
        (date(2014, 4, 1), date(2014, 5, 1)),
        (date(2014, 5, 1), date(2014, 6, 1)),
    ]
    assert interval_tuples(date(2014, 3, 5), date(2014, 5, 5), 'year') == [
        (date(2014, 3, 5), date(2015, 1, 1)),
    ]
    assert interval_tuples(date(2014, 1, 1), date(2015, 1, 1), 'year') == [
        (date(2014, 1, 1), date(2015, 1, 1)),
    ]
    assert interval_tuples(None, None, None) == []


def test_daterange():
    assert daterange('2014') == daterange(2014)
    assert daterange(2014, 10, 3) == daterange('2014', '10', '3')
    assert daterange('2014') == (date(2014, 1, 1), date(2015, 1, 1))
    assert daterange('2014', 10) == (date(2014, 10, 1), date(2014, 11, 1))
    assert daterange('2014', 10, 3) == (date(2014, 10, 3), date(2014, 10, 4))
    assert not daterange(None, 10, 10)


def test___parse_month():
    assert _parse_month('april') == 4
    assert _parse_month('apr') == 4
    assert _parse_month('october') == 10
    assert not _parse_month('test')


def to_date(string):
    if string is None:
        return None
    return dt.strptime(string, '%Y-%m-%d').date()


@pytest.mark.parametrize("pseudo_today,expect_start,expect_end,text", [
    (None, None, None, '    '),
    (None, '2010-10-01', '2010-11-01', 'october 2010       '),
    (None, '2000-01-01', '2001-01-01', '2000'),
    (None, '2008-02-01', '2008-02-02', '1st february 2008'),
    (None, '2010-10-01', '2010-11-01', '2010-10'),
    (None, '2000-01-03', '2000-01-04', '2000-01-03'),
    (None, '2010-08-02', '2010-08-03', '2nd aug, 2010'),
    (None, '2012-08-03', '2012-08-04', 'august 3rd, 2012'),
    (None, '2015-01-05', '2015-01-12', '2015-W01'),
    (None, '2015-04-01', '2015-07-01', '2015-Q2'),
    (None, '2014-01-01', '2016-01-01', '2014 to 2015'),
    (None, '2011-10-01', '2016-01-01', '2011-10 - 2015'),
    # use pseudo today
    ('2016-03-25', '2016-01-01', '2016-03-26', 'year to date'),
    ('2016-03-25', '2016-03-25', '2016-03-26', 'today'),
    ('2016-03-25', '2016-03-24', '2016-03-25', 'YESTERDAY'),
    ('2016-03-25', '2016-01-01', '2017-01-01', 'this year'),
    ('2016-03-25', '2017-08-01', '2017-09-01', 'august next year'),
    ('2016-03-25', '2016-03-01', '2016-04-01', 'this month'),
    ('2016-03-25', '2016-12-01', '2017-01-01', 'this december'),
    ('2016-03-25', '2016-11-01', '2016-12-01', 'this november'),
])
def test_parse_date(pseudo_today, expect_start, expect_end, text):
    today = to_date(pseudo_today)
    start, end = to_date(expect_start), to_date(expect_end)
    got = parse_date(text, today=today)
    assert got == (
        start, end
    ), "parse_date('%s', today=%s) == (%s, %s), want (%s, %s)" % (
        text, pseudo_today, got[0], got[1], expect_start, expect_end)


def test_number_of_days_in_period_daily():
    assert number_of_days_in_period('daily', dt(2016, 5, 1)) == 1
    assert number_of_days_in_period('daily', dt(2016, 5, 2)) == 1
    assert number_of_days_in_period('daily', dt(2016, 5, 31)) == 1


def test_number_of_days_in_period_weekly():
    assert number_of_days_in_period('weekly', dt(2016, 5, 1)) == 7
    assert number_of_days_in_period('weekly', dt(2016, 5, 2)) == 7
    assert number_of_days_in_period('weekly', dt(2016, 5, 31)) == 7


def test_number_of_days_in_period_monthly():
    assert number_of_days_in_period('monthly', dt(2016, 5, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 5, 2)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 5, 31)) == 31

    assert number_of_days_in_period('monthly', dt(2016, 6, 1)) == 30
    assert number_of_days_in_period('monthly', dt(2016, 6, 15)) == 30
    assert number_of_days_in_period('monthly', dt(2016, 6, 30)) == 30

    assert number_of_days_in_period('monthly', dt(2016, 7, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 7, 15)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 7, 31)) == 31

    assert number_of_days_in_period('monthly', dt(2016, 1, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 2, 1)) == 29
    assert number_of_days_in_period('monthly', dt(2016, 3, 31)) == 31


def test_number_of_days_in_period_quarterly():
    # 2016 = leap year
    assert number_of_days_in_period('quarterly', dt(2016, 2, 1)) == 91
    assert number_of_days_in_period('quarterly', dt(2016, 5, 30)) == 91
    assert number_of_days_in_period('quarterly', dt(2016, 8, 15)) == 92
    assert number_of_days_in_period('quarterly', dt(2016, 11, 15)) == 92

    # 2017 = not a leap year
    assert number_of_days_in_period('quarterly', dt(2017, 2, 1)) == 90
    assert number_of_days_in_period('quarterly', dt(2017, 5, 30)) == 91
    assert number_of_days_in_period('quarterly', dt(2017, 8, 15)) == 92
    assert number_of_days_in_period('quarterly', dt(2017, 11, 15)) == 92


def test_number_of_days_in_period_yearly():
    assert number_of_days_in_period('yearly', dt(2011, 2, 1)) == 365
    assert number_of_days_in_period('yearly', dt(2015, 5, 30)) == 365
    assert number_of_days_in_period('yearly', dt(2016, 8, 15)) == 366


def test_number_of_days_in_period_exception():
    with pytest.raises(Exception):
        number_of_days_in_period('test', dt(2011, 2, 1)) == 365
