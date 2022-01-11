"""Fava's options.

Options for Fava can be specified through Custom entries in the Beancount file.
This module contains a list of possible options, the defaults and the code for
parsing the options.

"""
from __future__ import annotations

import datetime
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import NamedTuple
from typing import Pattern

from babel.core import Locale  # type: ignore
from babel.core import UnknownLocaleError
from beancount.core.data import Custom

from fava.helpers import BeancountError
from fava.util.date import FiscalYearEnd
from fava.util.date import parse_fye_string


class OptionError(BeancountError):
    """An error for one the Fava options."""


class InsertEntryOption(NamedTuple):
    """Insert option.

    An option that determines where entries for matching accounts should be
    inserted.
    """

    date: datetime.date
    re: Pattern[str]
    filename: str
    lineno: int


@dataclass
class FavaOptions:
    """Options for Fava that can be set in the Beancount file."""

    # pylint: disable=too-many-instance-attributes

    account_journal_include_children: bool = True
    auto_reload: bool = False
    collapse_pattern: list[Pattern[str]] = field(default_factory=list)
    currency_column: int = 61
    default_file: str | None = None
    default_page: str = "income_statement/"
    fiscal_year_end: FiscalYearEnd = FiscalYearEnd(12, 31)
    import_config: str | None = None
    import_dirs: tuple[str, ...] = ()
    indent: int = 2
    insert_entry: list[InsertEntryOption] = field(default_factory=list)
    invert_income_liabilities_equity: bool = False
    journal_show: tuple[str, ...] = (
        "transaction",
        "balance",
        "note",
        "document",
        "custom",
        "budget",
        "query",
    )
    journal_show_document: tuple[str, ...] = ("discovered", "statement")
    journal_show_transaction: tuple[str, ...] = ("cleared", "pending")
    language: str | None = None
    locale: str | None = None
    show_accounts_with_zero_balance: bool = True
    show_accounts_with_zero_transactions: bool = True
    show_closed_accounts: bool = False
    sidebar_show_queries: int = 5
    unrealized: str = "Unrealized"
    upcoming_events: int = 7
    uptodate_indicator_grey_lookback_days: int = 60
    use_external_editor: bool = False

    asdict = asdict


_fields = fields(FavaOptions)
All_OPTS = {f.name for f in _fields}
BOOL_OPTS = {f.name for f in _fields if f.type == "bool"}  # type: ignore
INT_OPTS = {f.name for f in _fields if f.type == "int"}  # type: ignore
TUPLE_OPTS = {f.name for f in _fields if f.type.startswith("tuple[str,")}
STR_OPTS = {f.name for f in _fields if f.type.startswith("str")}


def parse_option_custom_entry(entry: Custom, options: FavaOptions) -> None:
    """Parse a single custom fava-option entry and set option accordingly."""
    key = entry.values[0].value.replace("-", "_")
    assert key in All_OPTS, f"unknown option `{key}`"

    if key == "default_file":
        options.default_file = entry.meta["filename"]
        return

    value = entry.values[1].value
    assert isinstance(value, str), f"expected string value for option `{key}`"

    if key == "insert_entry":
        try:
            pattern = re.compile(value)
        except re.error:
            assert False, f"Should be a regular expression: '{value}'."
        opt = InsertEntryOption(
            entry.date, pattern, entry.meta["filename"], entry.meta["lineno"]
        )
        options.insert_entry.append(opt)
    elif key == "collapse_pattern":
        try:
            pattern = re.compile(value)
        except re.error:
            assert False, f"Should be a regular expression: '{value}'."
        options.collapse_pattern.append(pattern)
    elif key == "locale":
        try:
            Locale.parse(value)
            options.locale = value
        except UnknownLocaleError:
            assert False, f"Unknown locale: '{value}'."
    elif key == "fiscal_year_end":
        fye = parse_fye_string(value)
        assert fye, "Invalid 'fiscal_year_end' option."
        options.fiscal_year_end = fye
    elif key in STR_OPTS:
        setattr(options, key, value)
    elif key in BOOL_OPTS:
        setattr(options, key, value.lower() == "true")
    elif key in INT_OPTS:
        setattr(options, key, int(value))
    else:
        assert key in TUPLE_OPTS, f"unknown option `{key}`"
        setattr(options, key, tuple(value.strip().split(" ")))


def parse_options(
    custom_entries: list[Custom],
) -> tuple[FavaOptions, list[OptionError]]:
    """Parse custom entries for Fava options.

    The format for option entries is the following::

        2016-04-01 custom "fava-option" "[name]" "[value]"

    Args:
        custom_entries: A list of Custom entries.

    Returns:
        A tuple (options, errors) where options is a dictionary of all options
        to values, and errors contains possible parsing errors.
    """

    options = FavaOptions()
    errors = []

    for entry in (e for e in custom_entries if e.type == "fava-option"):
        try:
            parse_option_custom_entry(entry, options)
        except (IndexError, TypeError, AssertionError) as err:
            msg = f"Failed to parse fava-option entry: {str(err)}"
            errors.append(OptionError(entry.meta, msg, entry))

    return options, errors
