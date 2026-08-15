from __future__ import annotations

import re
from datetime import date
from unittest import mock

import pytest

from fava.util.date import DateRange
from fava.util.date import END_OF_YEAR
from fava.util.date import FiscalYearEnd
from fava.util.date import parse_fye_string
from fava.util.date_parser import _DateExpressionParser
from fava.util.date_parser import parse_date


def date_range(begin: str, end: str) -> DateRange:
    return DateRange(date.fromisoformat(begin), date.fromisoformat(end))


MOCKED_TODAY = date.fromisoformat("2016-06-24")


@pytest.mark.parametrize(
    ("string", "expect_start", "expect_end"),
    [
        ("year", "2016-01-01", "2017-01-01"),
        ("(year-1)", "2015-01-01", "2016-01-01"),
        ("(YEAR+3)", "2019-01-01", "2020-01-01"),
        # 999 is the largest offset
        ("(year-999)", "1017-01-01", "1018-01-01"),
        ("quarter", "2016-04-01", "2016-07-01"),
        ("quarter+2", "2016-10-01", "2017-01-01"),
        ("quarter+20", "2021-04-01", "2021-07-01"),
        ("(month)", "2016-06-01", "2016-07-01"),
        ("month+6", "2016-12-01", "2017-01-01"),
        ("(MONTH+24)", "2018-06-01", "2018-07-01"),
        ("week", "2016-06-20", "2016-06-27"),
        ("week+20", "2016-11-07", "2016-11-14"),
        ("week+999", "2035-08-13", "2035-08-20"),
        ("day", "2016-06-24", "2016-06-25"),
        ("day+20", "2016-07-14", "2016-07-15"),
        # a variable can be refined further, like a literal year or month
        ("year-1-2", "2015-02-01", "2015-03-01"),
        ("(year)-1-2", "2016-01-02", "2016-01-03"),
        # the examples from the documentation
        ("month-10", "2015-08-01", "2015-09-01"),
        ("(month)-10", "2016-06-10", "2016-06-11"),
        ("year - day", "2016-01-01", "2016-06-25"),
        ("year-1 - year", "2015-01-01", "2017-01-01"),
    ],
)
def test_parse_date_variables(
    string: str,
    expect_start: str,
    expect_end: str,
) -> None:
    with mock.patch("fava.util.date_parser.local_today") as mock_local_today:
        mock_local_today.return_value = MOCKED_TODAY
        assert parse_date(string) == date_range(expect_start, expect_end)


NO_SUCH_PERIOD = "Date expression denotes a period that does not exist."


@pytest.mark.parametrize(
    ("string", "error"),
    [
        ("asdfasdf", "Unexpected 'a' in parsed expression."),
        ("2016-13", NO_SUCH_PERIOD),
        ("2016-02-30", NO_SUCH_PERIOD),
        ("2016-w99", NO_SUCH_PERIOD),
        ("2016-", "Unexpected 'end of input' in parsed expression."),
        ("(year", "Unexpected 'end of input' in parsed expression."),
        ("(2016)", "Unexpected '2016' in parsed expression."),
        ("(year 2016)", "Unexpected '2016' in parsed expression."),
        ("(year+3)month", "Unexpected 'month' in parsed expression."),
        ("2016 2017", "Unexpected '2017' in parsed expression."),
        ("q1", "Unexpected 'q1' in parsed expression."),
        ("2014 to 2015", "Unexpected 't' in parsed expression."),
        # only periods that are less specific than a day can be refined
        ("2016-q1-1", "Unexpected '1' in parsed expression."),
        ("2016--1", "Unexpected '-' in parsed expression."),
        ("2016-01--1", "Unexpected '-' in parsed expression."),
        ("fy2016-1", "Unexpected '1' in parsed expression."),
        # an offset of four or more digits is lexed as a year
        ("day+99999999", "Unexpected '+' in parsed expression."),
        ("week+2000", "Unexpected '+' in parsed expression."),
        ("(year-1000)", "Unexpected '-' in parsed expression."),
        # dates outside of the range that dates support
        ("0000", NO_SUCH_PERIOD),
        ("fy0000", NO_SUCH_PERIOD),
        # ranges that do not span at least one day
        ("2015 - 2014", "End date needs to be after begin date."),
        ("9999-12-31", "End date needs to be after begin date."),
    ],
)
def test_parse_date_invalid(string: str, error: str) -> None:
    with mock.patch("fava.util.date_parser.local_today") as mock_local_today:
        mock_local_today.return_value = MOCKED_TODAY
        assert parse_date(string) is None
        with pytest.raises(ValueError, match=f"^{re.escape(error)}$"):
            _DateExpressionParser(string, END_OF_YEAR).parse()


@pytest.mark.parametrize(
    ("fye_str", "test_date", "string", "expect_start", "expect_end"),
    [
        ("06-30", "2018-02-02", "fiscal_year", "2017-07-01", "2018-07-01"),
        ("06-30", "2018-08-02", "fiscal_year", "2018-07-01", "2019-07-01"),
        ("06-30", "2018-07-01", "fiscal_year", "2018-07-01", "2019-07-01"),
        ("06-30", "2018-08-02", "fiscal_year-1", "2017-07-01", "2018-07-01"),
        ("06-30", "2018-02-02", "fiscal_year+6", "2023-07-01", "2024-07-01"),
        ("06-30", "2018-08-02", "fiscal_year+6", "2024-07-01", "2025-07-01"),
        ("06-30", "2018-08-02", "fiscal_quarter", "2018-07-01", "2018-10-01"),
        ("06-30", "2018-10-01", "fiscal_quarter", "2018-10-01", "2019-01-01"),
        ("06-30", "2018-12-30", "fiscal_quarter", "2018-10-01", "2019-01-01"),
        ("06-30", "2018-02-02", "fiscal_quarter", "2018-01-01", "2018-04-01"),
        (
            "06-30",
            "2018-07-03",
            "fiscal_quarter-1",
            "2018-04-01",
            "2018-07-01",
        ),
        (
            "06-30",
            "2018-07-03",
            "fiscal_quarter+6",
            "2020-01-01",
            "2020-04-01",
        ),
        ("15-31", "2018-02-02", "fiscal_year", "2017-04-01", "2018-04-01"),
        ("15-31", "2018-05-02", "fiscal_year", "2018-04-01", "2019-04-01"),
        ("15-31", "2018-05-02", "fiscal_year-1", "2017-04-01", "2018-04-01"),
        ("15-31", "2018-02-02", "fiscal_year+6", "2023-04-01", "2024-04-01"),
        ("15-31", "2018-05-02", "fiscal_year+6", "2024-04-01", "2025-04-01"),
        ("15-31", "2018-02-02", "fiscal_quarter", "2018-01-01", "2018-04-01"),
        ("15-31", "2018-05-02", "fiscal_quarter", "2018-04-01", "2018-07-01"),
        ("15-31", "2018-08-02", "fiscal_quarter", "2018-07-01", "2018-10-01"),
        ("15-31", "2018-11-02", "fiscal_quarter", "2018-10-01", "2019-01-01"),
        (
            "15-31",
            "2018-05-02",
            "fiscal_quarter-1",
            "2018-01-01",
            "2018-04-01",
        ),
        (
            "15-31",
            "2018-05-02",
            "fiscal_quarter+6",
            "2019-10-01",
            "2020-01-01",
        ),
    ],
)
def test_parse_date_fiscal_variables(
    fye_str: str,
    test_date: str,
    string: str,
    expect_start: str,
    expect_end: str,
) -> None:
    fye = parse_fye_string(fye_str)
    with mock.patch("fava.util.date.datetime.date") as mock_date:
        mock_date.today.return_value = date.fromisoformat(test_date)
        mock_date.side_effect = date
        assert parse_date(string, fye) == date_range(expect_start, expect_end)


@pytest.mark.parametrize("string", ["fiscal_quarter", "fy2018-q1"])
def test_parse_date_fiscal_quarter_without_quarters(string: str) -> None:
    fye = parse_fye_string("04-05")
    assert fye is not None
    with mock.patch("fava.util.date_parser.local_today") as mock_local_today:
        mock_local_today.return_value = date.fromisoformat("2018-07-03")
        assert parse_date(string, fye) is None
        with pytest.raises(
            ValueError,
            match=f"^{re.escape(NO_SUCH_PERIOD)}$",
        ):
            _DateExpressionParser(string, fye).parse()


@pytest.mark.parametrize(
    ("expect_start", "expect_end", "text"),
    [
        ("2000-01-01", "2001-01-01", "   2000   "),
        ("2010-10-01", "2010-11-01", "2010-10"),
        ("2000-01-03", "2000-01-04", "2000-01-03"),
        ("2014-12-29", "2015-01-05", "2015-W01"),
        ("2024-12-30", "2025-01-06", "2025-W01"),
        ("2015-04-01", "2015-07-01", "2015-Q2"),
        ("2014-01-01", "2016-01-01", "2014-2015"),
        ("2011-10-01", "2016-01-01", "2011-10 - 2015"),
        ("2018-07-01", "2020-07-01", "FY2019 - FY2020"),
        ("2018-07-01", "2021-01-01", "FY2019 - 2020"),
        ("2010-07-01", "2015-07-01", "FY2011 - FY2015"),
        ("2011-01-01", "2015-07-01", "2011 - FY2015"),
    ],
)
def test_parse_date(expect_start: str, expect_end: str, text: str) -> None:
    expected = date_range(expect_start, expect_end)
    assert parse_date(text, FiscalYearEnd(6, 30)) == expected
    if "FY" not in text:
        assert parse_date(text, None) == expected


def test_parse_date_empty() -> None:
    assert parse_date("     ", FiscalYearEnd(6, 30)) is None
    assert parse_date("     ", None) is None


@pytest.mark.parametrize(
    ("expect_start", "expect_end", "text"),
    [
        ("2014-01-01", "2016-06-27", "year-2-day+2"),
        ("2016-01-01", "2016-06-25", "year-day"),
        ("2015-01-01", "2017-01-01", "2015-year"),
        ("2016-01-01", "2016-04-01", "quarter-1"),
        ("2013-07-01", "2014-07-01", "fiscal_year-2"),
        ("2016-04-01", "2016-07-01", "fiscal_quarter"),
    ],
)
def test_parse_date_relative(
    expect_start: str,
    expect_end: str,
    text: str,
) -> None:
    expected = date_range(expect_start, expect_end)
    with mock.patch("fava.util.date.datetime.date") as mock_date:
        mock_date.today.return_value = MOCKED_TODAY
        mock_date.side_effect = date
        assert parse_date(text, FiscalYearEnd(6, 30)) == expected
