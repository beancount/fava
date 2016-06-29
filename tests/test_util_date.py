from datetime import date, datetime

import pytest
from unittest import mock

from fava.util.date import (parse_date, get_next_interval, interval_tuples,
                            substitute, number_of_days_in_period)


def _to_date(string):
    """Convert a string in ISO 8601 format into a datetime.date object."""
    return datetime.strptime(string, '%Y-%m-%d').date() if string else None


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
    get = get_next_interval(_to_date(input_date_string), interval)
    assert get == _to_date(expect)


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


@pytest.mark.parametrize("expect_start,expect_end,text", [
    ('2014-01-01', '2016-06-27', 'year-2-day+2'),
    ('2016-01-01', '2016-06-25', 'year-day'),
])
def test_parse_date_relative(expect_start, expect_end, text):
    start, end = _to_date(expect_start), _to_date(expect_end)
    with mock.patch('fava.util.date.datetime.date') as mock_date:
        mock_date.today.return_value = _to_date('2016-06-24')
        mock_date.side_effect = date
        assert parse_date(text) == (start, end)


@pytest.mark.parametrize("interval,date,expect", [
    ('daily', '2016-05-01', 1),
    ('daily', '2016-05-31', 1),
    ('weekly', '2016-05-01', 7),
    ('weekly', '2016-05-31', 7),
    ('monthly', '2016-05-02', 31),
    ('monthly', '2016-05-31', 31),
    ('monthly', '2016-06-11', 30),
    ('monthly', '2016-07-31', 31),
    ('monthly', '2016-02-01', 29),
    ('monthly', '2015-02-01', 28),
    ('monthly', '2016-01-01', 31),
    ('quarterly', '2015-02-01', 90),
    ('quarterly', '2015-05-01', 91),
    ('quarterly', '2016-02-01', 91),
    ('quarterly', '2016-12-01', 92),
    ('yearly', '2015-02-01', 365),
    ('yearly', '2016-01-01', 366),
])
def test_number_of_days_in_period(interval, date, expect):
    assert number_of_days_in_period(interval, _to_date(date)) == expect


def test_number_of_days_in_period_exception():
    with pytest.raises(NotImplementedError):
        number_of_days_in_period('test', date(2011, 2, 1))
