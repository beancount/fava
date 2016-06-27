from datetime import date
from datetime import datetime as dt

import pytest
from unittest import mock

from fava.util.date import (parse_date, get_next_interval, interval_tuples,
                            substitute, number_of_days_in_period)


def _to_date(string):
    """Convert a string in ISO 8601 format into a datetime.date object."""
    return dt.strptime(string, '%Y-%m-%d').date() if string else None


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


@pytest.mark.parametrize("input,output", [
    ('year', '2016'),
    ('(year-1)', '2015'),
    ('year-1-2', '2015-2'),
    ('(year)-1-2', '2016-1-2'),
    ('(year+3)', '2019'),
    ('(year+3)month', '20192016-06'),
    ('(year-1000)', '1016'),
    ('quarter', '2016-Q2'),
    ('quarter+2', '2016-Q4'),
    ('quarter+20', '2021-Q2'),
    ('(month)', '2016-06'),
    ('month+6', '2016-12'),
    ('(month+24)', '2018-06'),
    ('week', '2016-W25'),
    ('week+20', '2016-W45'),
    ('week+2000', '2054-W42'),
    ('day', '2016-06-24'),
    ('day+20', '2016-07-14'),
])
def test_substitute(input, output):
    # Mock the imported datetime.date in fava.util.date module
    # Ref:
    # http://www.voidspace.org.uk/python/mock/examples.html#partial-mocking
    with mock.patch('fava.util.date.datetime.date') as mock_date:
        mock_date.today.return_value = _to_date('2016-06-24')
        mock_date.side_effect = date
        assert substitute(input) == output


@pytest.mark.parametrize("expect_start,expect_end,text", [
    (None, None, '    '),
    ('2000-01-01', '2001-01-01', '   2000   '),
    ('2010-10-01', '2010-11-01', '2010-10'),
    ('2000-01-03', '2000-01-04', '2000-01-03'),
    ('2015-01-05', '2015-01-12', '2015-W01'),
    ('2015-04-01', '2015-07-01', '2015-Q2'),
    ('2014-01-01', '2016-01-01', '2014 to 2015'),
    ('2014-01-01', '2016-01-01', '2014-2015'),
    ('2011-10-01', '2016-01-01', '2011-10 - 2015'),
])
def test_parse_date(expect_start, expect_end, text):
    start, end = _to_date(expect_start), _to_date(expect_end)
    assert parse_date(text) == (start, end)


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
