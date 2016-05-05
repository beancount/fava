import datetime
from datetime import datetime as dt

from fava.util.date import daterange, parse_date, number_of_days_in_period


def test_parse_date():
    today = datetime.date.today()
    tests = {
        'today': daterange(),
        'yesterday': daterange(timedelta=datetime.timedelta(days=-1)),
        'october 2010': daterange(2010, 10),
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
        '2015-W01': (datetime.date(2015, 1, 5), datetime.date(2015, 1, 12)),
        '2015-Q2': (datetime.date(2015, 4, 1), datetime.date(2015, 7, 1)),
        '2014 to 2015': (daterange(2014)[0], daterange(2015)[1]),
        '2011-10 - 2015': (daterange(2011, 10)[0], daterange(2015)[1]),
    }

    for test, result in tests.items():
        assert parse_date(test) == result


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
    assert number_of_days_in_period('quarterly', dt(2016, 2, 1)) == 90
    assert number_of_days_in_period('quarterly', dt(2016, 5, 30)) == 92
    assert number_of_days_in_period('quarterly', dt(2016, 8, 15)) == 92
    assert number_of_days_in_period('quarterly', dt(2016, 11, 15)) == 92


def test_number_of_days_in_period_yearly():
    assert number_of_days_in_period('yearly', dt(2011, 2, 1)) == 365
    assert number_of_days_in_period('yearly', dt(2015, 5, 30)) == 365
    assert number_of_days_in_period('yearly', dt(2016, 8, 15)) == 366
