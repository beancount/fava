from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from fava.util.date import DateRange
from fava.util.date import dateranges
from fava.util.date import Day
from fava.util.date import END_OF_YEAR
from fava.util.date import get_fiscal_period
from fava.util.date import interval_ends
from fava.util.date import INTERVALS
from fava.util.date import InvalidDateRangeError
from fava.util.date import Month
from fava.util.date import month_offset
from fava.util.date import parse_fye_string
from fava.util.date import Quarter
from fava.util.date import Week
from fava.util.date import Year

if TYPE_CHECKING:
    from fava.util.date import Interval


fromisoformat = date.fromisoformat


def test_interval() -> None:
    assert INTERVALS.get("month") is Month
    assert INTERVALS.get("year") is Year
    assert INTERVALS.get("asdfasdf") is None
    assert Year.label
    assert Quarter.label
    assert Month.label
    assert Week.label
    assert Day.label


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-01"),
        ("2016-01-04", Week, "2016-W01"),
        ("2016-01-04", Month, "2016-01"),
        ("2016-01-04", Quarter, "2016-Q1"),
        ("2016-01-04", Year, "2016"),
    ],
)
def test_interval_format(
    input_date_string: str,
    interval: Interval,
    expect: str,
) -> None:
    assert interval.format_date(fromisoformat(input_date_string)) == expect


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-02"),
        ("2016-01-01", Week, "2016-01-04"),
        ("2016-01-01", Month, "2016-02-01"),
        ("2016-01-01", Quarter, "2016-04-01"),
        ("2016-01-01", Year, "2017-01-01"),
        ("2016-12-31", Day, "2017-01-01"),
        ("2016-12-31", Week, "2017-01-02"),
        ("2016-12-31", Month, "2017-01-01"),
        ("2016-12-31", Quarter, "2017-01-01"),
        ("2016-12-31", Year, "2017-01-01"),
    ],
)
def test_get_next_interval(
    input_date_string: str,
    interval: Interval,
    expect: str,
) -> None:
    res = interval.get_next(fromisoformat(input_date_string))
    assert res == fromisoformat(expect)


def test_get_next_interval_max() -> None:
    for interval in set(INTERVALS.values()):
        assert interval.get_next(date.max) == date.max


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-01"),
        ("2016-01-01", Week, "2015-12-28"),
        ("2016-01-01", Month, "2016-01-01"),
        ("2016-01-01", Quarter, "2016-01-01"),
        ("2016-01-01", Year, "2016-01-01"),
        ("2016-12-31", Day, "2016-12-31"),
        ("2016-12-31", Week, "2016-12-26"),
        ("2016-12-31", Month, "2016-12-01"),
        ("2016-12-31", Quarter, "2016-10-01"),
        ("2016-12-31", Year, "2016-01-01"),
        ("2016-04-01", Quarter, "2016-04-01"),
        ("2016-04-15", Quarter, "2016-04-01"),
        ("2016-07-01", Quarter, "2016-07-01"),
        ("2016-09-30", Quarter, "2016-07-01"),
        ("2016-10-01", Quarter, "2016-10-01"),
        ("9999-12-31", Quarter, "9999-10-01"),
        ("9999-12-31", Year, "9999-01-01"),
    ],
)
def test_get_prev_interval(
    input_date_string: str,
    interval: Interval,
    expect: str,
) -> None:
    res = interval.get_prev(fromisoformat(input_date_string))
    assert res == fromisoformat(expect)


@pytest.mark.parametrize(
    ("begin", "end", "interval", "expect_complete", "expect_exact"),
    [
        (
            "2014-03-05",
            "2014-05-05",
            Month,
            [
                "2014-03-01",
                "2014-04-01",
                "2014-05-01",
                "2014-06-01",
            ],
            [
                "2014-03-05",
                "2014-04-01",
                "2014-05-01",
                "2014-05-05",
            ],
        ),
        (
            "2014-01-01",
            "2014-05-01",
            Month,
            [
                "2014-01-01",
                "2014-02-01",
                "2014-03-01",
                "2014-04-01",
                "2014-05-01",
            ],
            [
                "2014-01-01",
                "2014-02-01",
                "2014-03-01",
                "2014-04-01",
                "2014-05-01",
            ],
        ),
        (
            "2014-03-05",
            "2014-05-05",
            Year,
            [
                "2014-01-01",
                "2015-01-01",
            ],
            [
                "2014-03-05",
                "2014-05-05",
            ],
        ),
        (
            "2014-01-01",
            "2014-05-01",
            Year,
            [
                "2014-01-01",
                "2015-01-01",
            ],
            [
                "2014-01-01",
                "2014-05-01",
            ],
        ),
    ],
)
def test_interval_tuples(
    begin: str,
    end: str,
    interval: Interval,
    expect_complete: list[str],
    expect_exact: list[str],
) -> None:
    begin_date = fromisoformat(begin)
    end_date = fromisoformat(end)
    assert list(
        interval_ends(begin_date, end_date, interval, complete=True),
    ) == [fromisoformat(d) for d in expect_complete]
    assert list(
        interval_ends(begin_date, end_date, interval, complete=False),
    ) == [fromisoformat(d) for d in expect_exact]


def test_dateranges_single_date() -> None:
    date_ = date(2012, 1, 1)
    with pytest.raises(InvalidDateRangeError):
        DateRange(date_, date_)
    with pytest.raises(InvalidDateRangeError):
        list(interval_ends(date_, date_, Month, complete=True))
    with pytest.raises(InvalidDateRangeError):
        dateranges(date_, date_, Month, complete=True)


@pytest.mark.parametrize(
    ("interval", "date_str", "expect"),
    [
        (Day, "2016-05-01", 1),
        (Day, "2016-05-31", 1),
        (Week, "2016-05-01", 7),
        (Week, "2016-05-31", 7),
        (Month, "2016-05-02", 31),
        (Month, "2016-05-31", 31),
        (Month, "2016-06-11", 30),
        (Month, "2016-07-31", 31),
        (Month, "2016-02-01", 29),
        (Month, "2015-02-01", 28),
        (Month, "2016-01-01", 31),
        (Quarter, "2015-02-01", 90),
        (Quarter, "2015-05-01", 91),
        (Quarter, "2016-02-01", 91),
        (Quarter, "2016-12-01", 92),
        (Year, "2015-02-01", 365),
        (Year, "2016-01-01", 366),
        # dates in the first month of a quarter
        (Quarter, "2015-04-01", 91),
        (Quarter, "2015-07-01", 92),
        (Quarter, "2016-10-15", 92),
    ],
)
def test_number_of_days_in_period(
    interval: Interval,
    date_str: str,
    expect: int,
) -> None:
    assert interval.number_of_days(fromisoformat(date_str)) == expect


@pytest.mark.parametrize(
    ("date_input", "offset", "expected"),
    [
        ("2018-01-12", 0, "2018-01-12"),
        ("2018-01-01", -3, "2017-10-01"),
        ("2018-01-30", 1, None),  # raises value error, as it should
        ("2018-01-12", 13, "2019-02-12"),
        ("2018-01-12", -13, "2016-12-12"),
    ],
)
def test_month_offset(
    date_input: str,
    offset: int,
    expected: str | None,
) -> None:
    start_date = fromisoformat(date_input)
    if expected is None:
        with pytest.raises(ValueError, match=r"day .* range"):
            month_offset(start_date, offset)
    else:
        assert str(month_offset(start_date, offset)) == expected


@pytest.mark.parametrize(
    ("year", "quarter", "fye_str", "expect_start", "expect_end"),
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
        # 28th February - consider leap years [FYE=02-28]
        (2016, None, "02-28", "2015-03-01", "2016-03-01"),
        (2017, None, "02-28", "2016-03-01", "2017-03-01"),
        # 1st Apr (last year) - JP [FYE=15-31]
        (2018, None, "15-31", "2018-04-01", "2019-04-01"),
        (2018, 1, "15-31", "2018-04-01", "2018-07-01"),
        (2018, 4, "15-31", "2019-01-01", "2019-04-01"),
        # None
        (2018, None, None, "2018-01-01", "2019-01-01"),
    ],
)
def test_get_fiscal_period(
    year: int,
    quarter: int | None,
    fye_str: str | None,
    expect_start: str,
    expect_end: str,
) -> None:
    fye = parse_fye_string(fye_str) if fye_str else None
    start_date, end_date = get_fiscal_period(year, fye or END_OF_YEAR, quarter)
    assert str(start_date) == expect_start
    assert str(end_date) == expect_end


@pytest.mark.parametrize(
    ("year", "quarter", "fye_str", "msg"),
    [
        (2018, 0, "12-31", "quarter must be in 1..4"),
        (2018, 5, "12-31", "quarter must be in 1..4"),
        # 5th Apr - UK [FYE=04-05]
        (2018, 1, "04-05", "fiscal year does not start on first"),
    ],
)
def test_get_fiscal_period_errors(
    year: int, quarter: int, fye_str: str, msg: str
) -> None:
    fye = parse_fye_string(fye_str)
    assert fye
    with pytest.raises(ValueError, match=msg):
        get_fiscal_period(year, fye, quarter)


@pytest.mark.parametrize(
    ("fye_str", "month", "day"),
    [
        ("12-31", 12, 31),
        ("06-30", 6, 30),
        ("02-28", 2, 28),
        ("15-31", 15, 31),
    ],
)
def test_parse_fye_string(fye_str: str, month: int, day: int) -> None:
    fye = parse_fye_string(fye_str)
    assert fye
    assert fye.month == month
    assert fye.day == day


@pytest.mark.parametrize(
    "fye_str",
    [
        "12-32",
        "asdfasdf",
        "02-29",
    ],
)
def test_parse_fye_invalid_string(fye_str: str) -> None:
    assert parse_fye_string(fye_str) is None
