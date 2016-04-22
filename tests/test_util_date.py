from datetime import date, timedelta

import pytest

from fava.util.date import (_parse_month, parse_date, daterange,
                            get_next_interval, interval_tuples)


def test_get_next_interval():
    assert get_next_interval(date(2013, 12, 31), 'year') == date(2014, 1, 1)
    assert get_next_interval(date(2013, 1, 1), 'year') == date(2014, 1, 1)
    assert get_next_interval(date(2013, 1, 1), 'quarter') == date(2013, 4, 1)
    assert get_next_interval(date(2013, 1, 1), 'month') == date(2013, 2, 1)
    assert get_next_interval(date(2016, 4, 17), 'week') == date(2016, 4, 18)
    assert get_next_interval(date(2016, 4, 17), 'day') == date(2016, 4, 18)
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


def test_parse_date():
    today = date.today()
    tests = {
        'year to date': (date(today.year, 1, 1), today + timedelta(1)),
        '    ': (None, None),
        'today': (today, today + timedelta(1)),
        'YESTERDAY': (today - timedelta(1), today),
        'october 2010       ': daterange(2010, 10),
        '2000': daterange(2000),
        '1st february 2008': daterange(2008, 2, 1),
        '2010-10': daterange(2010, 10),
        '2000-01-03': daterange(2000, 1, 3),
        'this year': daterange(today.year),
        'august next year': daterange(today.year + 1, 8),
        'this month': daterange(today.year, today.month),
        'this december': daterange(today.year, 12),
        'this november': daterange(today.year, 11),
        '2nd aug, 2010': daterange(2010, 8, 2),
        'august 3rd, 2012': daterange(2012, 8, 3),
        '2015-W01': (date(2015, 1, 5), date(2015, 1, 12)),
        '2015-Q2': (date(2015, 4, 1), date(2015, 7, 1)),
        '2014 to 2015': (daterange(2014)[0], daterange(2015)[1]),
        '2011-10 - 2015': (daterange(2011, 10)[0], daterange(2015)[1]),
    }
    for test, result in tests.items():
        assert parse_date(test) == result
