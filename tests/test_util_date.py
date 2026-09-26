from __future__ import annotations

from datetime import date
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from fava.util.date import DateRange
from fava.util.date import dateranges
from fava.util.date import Day
from fava.util.date import END_OF_YEAR
from fava.util.date import FiscalQuarter
from fava.util.date import FiscalYear
from fava.util.date import FiscalYearEnd
from fava.util.date import FiscalYearEnds
from fava.util.date import Fortnight
from fava.util.date import FyeHasNoQuartersError
from fava.util.date import get_budget_interval
from fava.util.date import get_interval
from fava.util.date import interval_ends
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
    assert get_interval("month", END_OF_YEAR) is Month
    assert get_interval("year", END_OF_YEAR) is Year
    assert get_interval("asdfasdf", END_OF_YEAR) is None
    assert Year.label
    assert Quarter.label
    assert Month.label
    assert Week.label
    assert Day.label
    assert FiscalYear(FiscalYearEnds.UK).label
    assert FiscalQuarter(FiscalYearEnds.AU_NZ).label
    assert hash(FiscalYearEnds.UK)
    assert parse_fye_string("04-05") == FiscalYearEnds.UK


def test_get_interval_fiscal() -> None:
    assert get_interval("fiscal_year", END_OF_YEAR) is None
    assert get_interval("fiscal_quarter", END_OF_YEAR) is None
    assert get_interval("fiscal_year", FiscalYearEnds.UK) == FiscalYear(
        FiscalYearEnds.UK
    )
    assert get_interval(
        "fiscal_quarter", FiscalYearEnds.AU_NZ
    ) == FiscalQuarter(FiscalYearEnds.AU_NZ)
    assert get_interval("asdf", FiscalYearEnds.UK) is None
    assert get_interval("fiscal_quarter", FiscalYearEnds.UK) is None
    assert get_interval("FISCAL_YEAR", FiscalYearEnds.UK) == FiscalYear(
        FiscalYearEnds.UK
    )


@pytest.mark.parametrize(
    ("fye", "input_date_string", "expect"),
    [
        (END_OF_YEAR, "2023-01-01", 2023),
        (END_OF_YEAR, "2023-12-31", 2023),
        (FiscalYearEnds.ZA, "2023-02-28", 2023),
        (FiscalYearEnds.ZA, "2023-03-01", 2024),
        (FiscalYearEnds.UK, "2024-04-05", 2024),
        (FiscalYearEnds.UK, "2024-04-06", 2025),
        (FiscalYearEnds.JP, "2024-02-02", 2023),
        (FiscalYearEnds.JP, "2024-03-31", 2023),
        (FiscalYearEnds.JP, "2024-04-01", 2024),
    ],
)
def test_fye_get_fiscal_year_from_date(
    fye: FiscalYearEnd, input_date_string: str, expect: int
) -> None:
    assert fye.fiscal_year(fromisoformat(input_date_string)) == expect


def test_fortnight_is_budget_only() -> None:
    assert get_interval("fortnightly", END_OF_YEAR) is None
    assert get_budget_interval("fortnightly", END_OF_YEAR) is Fortnight
    assert get_budget_interval("Fortnight", END_OF_YEAR) is Fortnight
    assert get_budget_interval("weekly", END_OF_YEAR) is Week
    assert get_budget_interval("fiscal_year", FiscalYearEnds.UK) == FiscalYear(
        FiscalYearEnds.UK
    )
    assert get_budget_interval("asdf", END_OF_YEAR) is None
    assert Fortnight.label


def test_fortnight_blocks_are_fixed_14_days() -> None:
    # 2020 has 53 ISO weeks; fortnights must stay contiguous and 14 days
    # long across it rather than shrinking to a single week.
    start = Fortnight.get_prev(date(2020, 12, 21))
    for _ in range(6):
        end = Fortnight.get_next(start)
        assert (end - start).days == 14
        assert start.weekday() == 0
        for offset in range(14):
            day = start + timedelta(offset)
            assert Fortnight.get_prev(day) == start
            assert Fortnight.number_of_days(day) == 14
        start = end
    assert Fortnight.get_next(date.max) == date.max


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-01"),
        ("2016-01-04", Week, "2016-W01"),
        ("2016-01-04", Fortnight, "2016-01-04"),
        ("2016-01-10", Fortnight, "2016-01-04"),
        ("2016-01-04", Month, "2016-01"),
        ("2016-01-04", Quarter, "2016-Q1"),
        ("2016-03-31", Quarter, "2016-Q1"),
        ("2016-04-01", Quarter, "2016-Q2"),
        ("2016-01-04", Year, "2016"),
        ("0999-01-04", Day, "0999-01-04"),
        ("0999-01-04", Week, "0999-W01"),
        ("0999-01-04", Month, "0999-01"),
        ("0999-01-04", Quarter, "0999-Q1"),
        ("0999-01-04", Year, "0999"),
        ("0999-01-04", FiscalYear(FiscalYearEnds.UK), "FY0999"),
        ("0999-04-06", FiscalQuarter(FiscalYearEnds.AU_NZ), "FY0999-Q4"),
        ("2016-01-04", FiscalYear(FiscalYearEnds.UK), "FY2016"),
        ("2016-04-06", FiscalYear(FiscalYearEnds.UK), "FY2017"),
        ("2016-04-06", FiscalQuarter(FiscalYearEnds.AU_NZ), "FY2016-Q4"),
        ("2016-01-01", FiscalQuarter(FiscalYearEnds.AU_NZ), "FY2016-Q3"),
        ("2015-10-02", FiscalQuarter(FiscalYearEnds.AU_NZ), "FY2016-Q2"),
        ("2015-11-01", FiscalQuarter(FiscalYearEnds.JP), "FY2015-Q3"),
        ("2016-02-01", FiscalQuarter(FiscalYearEnds.JP), "FY2015-Q4"),
    ],
)
def test_interval_format(
    input_date_string: str, interval: Interval, expect: str
) -> None:
    assert interval.format_date(fromisoformat(input_date_string)) == expect


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-02"),
        ("2016-01-01", Week, "2016-01-04"),
        ("2016-01-01", Fortnight, "2016-01-04"),
        ("2016-12-31", Fortnight, "2017-01-02"),
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
    input_date_string: str, interval: Interval, expect: str
) -> None:
    res = interval.get_next(fromisoformat(input_date_string))
    assert res == fromisoformat(expect)


def test_get_next_interval_max() -> None:
    assert Day.get_next(date.max) == date.max
    assert Week.get_next(date.max) == date.max
    assert Month.get_next(date.max) == date.max
    assert Quarter.get_next(date.max) == date.max
    assert Year.get_next(date.max) == date.max
    assert FiscalQuarter(FiscalYearEnds.JP).get_next(date.max) == date.max
    assert FiscalYear(FiscalYearEnds.JP).get_next(date.max) == date.max


@pytest.mark.parametrize(
    ("input_date_string", "interval", "expect"),
    [
        ("2016-01-01", Day, "2016-01-01"),
        ("2016-01-01", Week, "2015-12-28"),
        ("2016-01-01", Fortnight, "2015-12-21"),
        ("2016-12-31", Fortnight, "2016-12-19"),
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
    input_date_string: str, interval: Interval, expect: str
) -> None:
    res = interval.get_prev(fromisoformat(input_date_string))
    assert res == fromisoformat(expect)


@pytest.mark.parametrize(
    ("input_date_string", "fye", "expect"),
    [
        ("2016-01-01", FiscalYearEnds.ZA, "2015-03-01"),
        ("2016-02-28", FiscalYearEnds.ZA, "2015-03-01"),
        ("2016-02-29", FiscalYearEnds.ZA, "2015-03-01"),
        ("2016-03-01", FiscalYearEnds.ZA, "2016-03-01"),
        ("2016-01-01", FiscalYearEnds.UK, "2015-04-06"),
        ("2016-02-28", FiscalYearEnds.UK, "2015-04-06"),
        ("2016-06-01", FiscalYearEnds.UK, "2016-04-06"),
        ("2016-01-01", FiscalYearEnds.JP, "2015-04-01"),
        ("2016-02-28", FiscalYearEnds.JP, "2015-04-01"),
        ("2016-06-01", FiscalYearEnds.JP, "2016-04-01"),
        ("2016-01-01", END_OF_YEAR, "2016-01-01"),
        ("2016-12-31", END_OF_YEAR, "2016-01-01"),
    ],
)
def test_get_prev_interval_fiscal_year(
    input_date_string: str, fye: FiscalYearEnd, expect: str
) -> None:
    interval = FiscalYear(fye)
    input_date = fromisoformat(input_date_string)
    expect_date = fromisoformat(expect)
    assert interval.get_prev(input_date) == expect_date
    assert interval.get_next(input_date) == expect_date.replace(
        year=expect_date.year + 1
    )


@pytest.mark.parametrize(
    ("begin", "end", "interval", "expect_complete", "expect_exact"),
    [
        (
            "2014-03-05",
            "2014-05-05",
            Month,
            ["2014-03-01", "2014-04-01", "2014-05-01", "2014-06-01"],
            ["2014-03-05", "2014-04-01", "2014-05-01", "2014-05-05"],
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
            ["2014-01-01", "2015-01-01"],
            ["2014-03-05", "2014-05-05"],
        ),
        (
            "2014-01-01",
            "2014-05-01",
            Year,
            ["2014-01-01", "2015-01-01"],
            ["2014-01-01", "2014-05-01"],
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
        (Quarter, "2015-04-01", 91),
        (Quarter, "2015-05-01", 91),
        (Quarter, "2015-07-01", 92),
        (Quarter, "2016-02-01", 91),
        (Quarter, "2016-10-15", 92),
        (Quarter, "2016-12-01", 92),
        (Year, "2015-02-01", 365),
        (Year, "2016-01-01", 366),
    ],
)
def test_number_of_days_in_period(
    interval: Interval, date_str: str, expect: int
) -> None:
    assert interval.number_of_days(fromisoformat(date_str)) == expect


@pytest.mark.parametrize(
    ("date_input", "offset", "expected"),
    [
        ("2018-01-01", 0, "2018-01-01"),
        ("2018-01-01", -3, "2017-10-01"),
        ("2018-01-01", 13, "2019-02-01"),
        ("2018-01-01", -13, "2016-12-01"),
    ],
)
def test_month_offset(date_input: str, offset: int, expected: str) -> None:
    start_date = fromisoformat(date_input)
    assert month_offset(start_date, offset) == fromisoformat(expected)


@pytest.mark.parametrize(
    ("year", "fye", "expect_start"),
    [
        (2018, END_OF_YEAR, "2018-01-01"),
        (2018, FiscalYearEnds.US, "2017-10-01"),
        (2018, FiscalYearEnds.AU_NZ, "2017-07-01"),
        (2018, FiscalYearEnds.UK, "2017-04-06"),
        (2016, FiscalYearEnds.ZA, "2015-03-01"),
        (2017, FiscalYearEnds.ZA, "2016-03-01"),
        (2018, FiscalYearEnds.JP, "2018-04-01"),
    ],
)
def test_get_fiscal_period(
    year: int, fye: FiscalYearEnd, expect_start: str
) -> None:
    begin = fye.begin_date_for_year(year)
    assert str(begin) == expect_start


@pytest.mark.parametrize(
    ("input_date_string", "fye", "expect_start"),
    [
        ("2018-01-01", END_OF_YEAR, "2018-01-01"),
        ("2018-08-15", END_OF_YEAR, "2018-07-01"),
        ("2018-12-31", END_OF_YEAR, "2018-10-01"),
        ("2018-05-20", FiscalYearEnds.US, "2018-04-01"),
        ("2018-07-01", FiscalYearEnds.AU_NZ, "2018-07-01"),
        ("2018-06-30", FiscalYearEnds.AU_NZ, "2018-04-01"),
        ("2018-11-30", FiscalYearEnds.AU_NZ, "2018-10-01"),
        ("2018-12-31", FiscalYearEnds.JP, "2018-10-01"),
        ("2019-01-01", FiscalYearEnds.JP, "2019-01-01"),
    ],
)
def test_fiscal_quarter_get_prev(
    input_date_string: str, fye: FiscalYearEnd, expect_start: str
) -> None:
    interval = FiscalQuarter(fye)
    res = interval.get_prev(fromisoformat(input_date_string))
    assert res == fromisoformat(expect_start)


def test_fiscal_quarter_without_quarters() -> None:
    with pytest.raises(FyeHasNoQuartersError):
        FiscalQuarter(FiscalYearEnds.UK)


def test_fiscal_year_end() -> None:
    with pytest.raises(ValueError, match="Invalid fiscal year end month"):
        FiscalYearEnd(0, 12)
    with pytest.raises(ValueError, match="Invalid fiscal year end month"):
        FiscalYearEnd(25, 12)


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
