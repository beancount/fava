# pylint: disable=missing-docstring
from datetime import date
from datetime import datetime
from typing import Optional
from typing import Tuple
from unittest import mock

import pytest

from fava.util.date import FiscalYearEnd
from fava.util.date import get_fiscal_period
from fava.util.date import get_next_interval
from fava.util.date import Interval
from fava.util.date import interval_ends
from fava.util.date import month_offset
from fava.util.date import number_of_days_in_period
from fava.util.date import parse_date
from fava.util.date import parse_fye_string
from fava.util.date import substitute


def test_interval():
    assert Interval.get("month") is Interval.MONTH
    assert Interval.get("year") is Interval.YEAR
    assert Interval.get("YEAR") is Interval.YEAR
    assert Interval.get("asdfasdf") is Interval.MONTH


def _to_date(string):
    """Convert a string in ISO 8601 format into a datetime.date object."""
    return datetime.strptime(string, "%Y-%m-%d").date() if string else None


@pytest.mark.parametrize(
    "input_date_string,interval,expect",
    [
        ("2016-01-01", Interval.DAY, "2016-01-02"),
        ("2016-01-01", Interval.WEEK, "2016-01-04"),
        ("2016-01-01", Interval.MONTH, "2016-02-01"),
        ("2016-01-01", Interval.QUARTER, "2016-04-01"),
        ("2016-01-01", Interval.YEAR, "2017-01-01"),
        ("2016-12-31", Interval.DAY, "2017-01-01"),
        ("2016-12-31", Interval.WEEK, "2017-01-02"),
        ("2016-12-31", Interval.MONTH, "2017-01-01"),
        ("2016-12-31", Interval.QUARTER, "2017-01-01"),
        ("2016-12-31", Interval.YEAR, "2017-01-01"),
        ("9999-12-31", Interval.QUARTER, "9999-12-31"),
        ("9999-12-31", Interval.YEAR, "9999-12-31"),
    ],
)
def test_get_next_interval(input_date_string, interval, expect):
    get = get_next_interval(_to_date(input_date_string), interval)
    assert get == _to_date(expect)


def test_get_next_intervalfail2():
    with pytest.raises(NotImplementedError):
        get_next_interval(date(2016, 4, 18), "decade")


def test_interval_tuples():
    assert list(
        interval_ends(date(2014, 3, 5), date(2014, 5, 5), Interval.MONTH)
    ) == [
        date(2014, 3, 5),
        date(2014, 4, 1),
        date(2014, 5, 1),
        date(2014, 5, 5),
    ]
    assert list(
        interval_ends(date(2014, 1, 1), date(2014, 5, 1), Interval.MONTH)
    ) == [
        date(2014, 1, 1),
        date(2014, 2, 1),
        date(2014, 3, 1),
        date(2014, 4, 1),
        date(2014, 5, 1),
    ]
    assert list(
        interval_ends(date(2014, 3, 5), date(2014, 5, 5), Interval.YEAR)
    ) == [date(2014, 3, 5), date(2014, 5, 5)]
    assert list(
        interval_ends(date(2014, 1, 1), date(2015, 1, 1), Interval.YEAR)
    ) == [date(2014, 1, 1), date(2015, 1, 1)]


@pytest.mark.parametrize(
    "string,output",
    [
        ("year", "2016"),
        ("(year-1)", "2015"),
        ("year-1-2", "2015-2"),
        ("(year)-1-2", "2016-1-2"),
        ("(year+3)", "2019"),
        ("(year+3)month", "20192016-06"),
        ("(year-1000)", "1016"),
        ("quarter", "2016-Q2"),
        ("quarter+2", "2016-Q4"),
        ("quarter+20", "2021-Q2"),
        ("(month)", "2016-06"),
        ("month+6", "2016-12"),
        ("(month+24)", "2018-06"),
        ("week", "2016-W25"),
        ("week+20", "2016-W45"),
        ("week+2000", "2054-W42"),
        ("day", "2016-06-24"),
        ("day+20", "2016-07-14"),
    ],
)
def test_substitute(string, output):
    # Mock the imported datetime.date in fava.util.date module
    # Ref:
    # http://www.voidspace.org.uk/python/mock/examples.html#partial-mocking
    with mock.patch("fava.util.date.datetime.date") as mock_date:
        mock_date.today.return_value = _to_date("2016-06-24")
        mock_date.side_effect = date
        assert substitute(string) == output


@pytest.mark.parametrize(
    "fye,test_date,string,output",
    [
        ("06-30", "2018-02-02", "fiscal_year", "FY2018"),
        ("06-30", "2018-08-02", "fiscal_year", "FY2019"),
        ("06-30", "2018-07-01", "fiscal_year", "FY2019"),
        ("06-30", "2018-08-02", "fiscal_year-1", "FY2018"),
        ("06-30", "2018-02-02", "fiscal_year+6", "FY2024"),
        ("06-30", "2018-08-02", "fiscal_year+6", "FY2025"),
        ("06-30", "2018-08-02", "fiscal_quarter", "FY2019-Q1"),
        ("06-30", "2018-10-01", "fiscal_quarter", "FY2019-Q2"),
        ("06-30", "2018-12-30", "fiscal_quarter", "FY2019-Q2"),
        ("06-30", "2018-02-02", "fiscal_quarter", "FY2018-Q3"),
        ("06-30", "2018-07-03", "fiscal_quarter-1", "FY2018-Q4"),
        ("06-30", "2018-07-03", "fiscal_quarter+6", "FY2020-Q3"),
        ("04-05", "2018-07-03", "fiscal_quarter", None),
    ],
)
def test_fiscal_substitute(fye, test_date, string, output):
    fye = parse_fye_string(fye)
    with mock.patch("fava.util.date.datetime.date") as mock_date:
        mock_date.today.return_value = _to_date(test_date)
        mock_date.side_effect = date
        if output is None:
            with pytest.raises(ValueError):
                substitute(string, fye)
        else:
            assert substitute(string, fye) == output


@pytest.mark.parametrize(
    "expect_start,expect_end,text",
    [
        (None, None, "    "),
        ("2000-01-01", "2001-01-01", "   2000   "),
        ("2010-10-01", "2010-11-01", "2010-10"),
        ("2000-01-03", "2000-01-04", "2000-01-03"),
        ("2015-01-05", "2015-01-12", "2015-W01"),
        ("2015-04-01", "2015-07-01", "2015-Q2"),
        ("2014-01-01", "2016-01-01", "2014 to 2015"),
        ("2014-01-01", "2016-01-01", "2014-2015"),
        ("2011-10-01", "2016-01-01", "2011-10 - 2015"),
        ("2018-07-01", "2020-07-01", "FY2019 - FY2020"),
        ("2018-07-01", "2021-01-01", "FY2019 - 2020"),
        ("2010-07-01", "2015-07-01", "FY2011 to FY2015"),
        ("2011-01-01", "2015-07-01", "2011 to FY2015"),
    ],
)
def test_parse_date(expect_start, expect_end, text):
    start, end = _to_date(expect_start), _to_date(expect_end)
    assert parse_date(text, FiscalYearEnd(6, 30)) == (start, end)
    if "FY" not in text:
        assert parse_date(text, None) == (start, end)


@pytest.mark.parametrize(
    "expect_start,expect_end,text",
    [
        ("2014-01-01", "2016-06-27", "year-2-day+2"),
        ("2016-01-01", "2016-06-25", "year-day"),
        ("2015-01-01", "2017-01-01", "2015-year"),
        ("2016-01-01", "2016-04-01", "quarter-1"),
        ("2013-07-01", "2014-07-01", "fiscal_year-2"),
        ("2016-04-01", "2016-07-01", "fiscal_quarter"),
    ],
)
def test_parse_date_relative(expect_start, expect_end, text):
    start, end = _to_date(expect_start), _to_date(expect_end)
    with mock.patch("fava.util.date.datetime.date") as mock_date:
        mock_date.today.return_value = _to_date("2016-06-24")
        mock_date.side_effect = date
        assert parse_date(text, FiscalYearEnd(6, 30)) == (start, end)


@pytest.mark.parametrize(
    "interval,date_str,expect",
    [
        (Interval.DAY, "2016-05-01", 1),
        (Interval.DAY, "2016-05-31", 1),
        (Interval.WEEK, "2016-05-01", 7),
        (Interval.WEEK, "2016-05-31", 7),
        (Interval.MONTH, "2016-05-02", 31),
        (Interval.MONTH, "2016-05-31", 31),
        (Interval.MONTH, "2016-06-11", 30),
        (Interval.MONTH, "2016-07-31", 31),
        (Interval.MONTH, "2016-02-01", 29),
        (Interval.MONTH, "2015-02-01", 28),
        (Interval.MONTH, "2016-01-01", 31),
        (Interval.QUARTER, "2015-02-01", 90),
        (Interval.QUARTER, "2015-05-01", 91),
        (Interval.QUARTER, "2016-02-01", 91),
        (Interval.QUARTER, "2016-12-01", 92),
        (Interval.YEAR, "2015-02-01", 365),
        (Interval.YEAR, "2016-01-01", 366),
    ],
)
def test_number_of_days_in_period(interval, date_str, expect):
    assert number_of_days_in_period(interval, _to_date(date_str)) == expect


def test_number_of_days_in_period2():
    with pytest.raises(NotImplementedError):
        number_of_days_in_period("test", date(2011, 2, 1))


@pytest.mark.parametrize(
    "date_input,offset,expected",
    [
        ("2018-01-12", 0, "2018-01-12"),
        ("2018-01-01", -3, "2017-10-01"),
        ("2018-01-30", 1, None),  # raises value error, as it should
        ("2018-01-12", 13, "2019-02-12"),
        ("2018-01-12", -13, "2016-12-12"),
    ],
)
def test_month_offset(date_input, offset, expected):
    start_date = _to_date(date_input)
    if expected is None:
        with pytest.raises(ValueError):
            month_offset(start_date, offset)
    else:
        assert str(month_offset(start_date, offset)) == expected


@pytest.mark.parametrize(
    "year,quarter,fye,expect_start,expect_end",
    [
        # standard calendar year [FYE=12-31]
        (2018, None, "12-31", "2018-01-01", "2019-01-01"),
        (2018, 1, "12-31", "2018-01-01", "2018-04-01"),
        (2018, 3, "12-31", "2018-07-01", "2018-10-01"),
        (2018, 4, "12-31", "2018-10-01", "2019-01-01"),
        # US fiscal year [FYE=09-30]
        (2018, None, "09-30", "2017-10-01", "2018-10-01"),
        (2018, 3, "09-30", "2018-04-01", "2018-07-01"),
        # 30th June - Australia and NZ [FYE=06-30]
        (2018, None, "06-30", "2017-07-01", "2018-07-01"),
        (2018, 1, "06-30", "2017-07-01", "2017-10-01"),
        (2018, 2, "06-30", "2017-10-01", "2018-01-01"),
        (2018, 4, "06-30", "2018-04-01", "2018-07-01"),
        # 5th Apr - UK [FYE=04-05]
        (2018, None, "04-05", "2017-04-06", "2018-04-06"),
        (2018, 1, "04-05", "None", "None"),
        # 28th February - consider leap years [FYE=02-28]
        (2016, None, "02-28", "2015-03-01", "2016-03-01"),
        (2017, None, "02-28", "2016-03-01", "2017-03-01"),
        # None
        (2018, None, None, "2018-01-01", "2019-01-01"),
        # expected errors
        (2018, 0, "12-31", "None", "None"),
        (2018, 5, "12-31", "None", "None"),
    ],
)
def test_get_fiscal_period(year, quarter, fye, expect_start, expect_end):
    fye = parse_fye_string(fye)
    start_date, end_date = get_fiscal_period(year, fye, quarter)
    assert str(start_date) == expect_start
    assert str(end_date) == expect_end


@pytest.mark.parametrize(
    "fye,expected",
    [
        ("12-31", (12, 31)),
        ("06-30", (6, 30)),
        ("02-28", (2, 28)),
        ("12-32", None),
        ("asdfasdf", None),
        ("02-29", None),
    ],
)
def test_parse_fye_string(
    fye: str, expected: Optional[Tuple[int, int]]
) -> None:
    fye_tuple = parse_fye_string(fye)
    assert fye_tuple == expected
