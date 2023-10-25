"""Fava's options.

Options for Fava can be specified through Custom entries in the Beancount file.
This module contains a list of possible options, the defaults and the code for
parsing the options.

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Pattern
from typing import TYPE_CHECKING

from babel.core import Locale
from babel.core import UnknownLocaleError

from fava.helpers import BeancountError
from fava.util.date import END_OF_YEAR
from fava.util.date import parse_fye_string

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Custom
    from fava.util.date import FiscalYearEnd


class OptionError(BeancountError):
    """An error for one the Fava options."""


@dataclass(frozen=True)
class InsertEntryOption:
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

    account_journal_include_children: bool = True
    auto_reload: bool = False
    collapse_pattern: list[Pattern[str]] = field(default_factory=list)
    currency_column: int = 61
    conversion_currencies: tuple[str, ...] = ()
    default_file: str | None = None
    default_page: str = "income_statement/"
    fiscal_year_end: FiscalYearEnd = END_OF_YEAR
    import_config: str | None = None
    import_dirs: tuple[str, ...] = ()
    indent: int = 2
    insert_entry: list[InsertEntryOption] = field(default_factory=list)
    invert_income_liabilities_equity: bool = False
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


_fields = fields(FavaOptions)
All_OPTS = {f.name for f in _fields}
BOOL_OPTS = {f.name for f in _fields if str(f.type) == "bool"}
INT_OPTS = {f.name for f in _fields if str(f.type) == "int"}
TUPLE_OPTS = {f.name for f in _fields if f.type.startswith("tuple[str,")}
STR_OPTS = {f.name for f in _fields if f.type.startswith("str")}


def parse_option_custom_entry(  # noqa: PLR0912
    entry: Custom,
    options: FavaOptions,
) -> None:
    """Parse a single custom fava-option entry and set option accordingly."""
    key = entry.values[0].value.replace("-", "_")
    if key not in All_OPTS:
        raise ValueError(f"unknown option `{key}`")

    if key == "default_file":
        options.default_file = entry.meta["filename"]
        return

    value = entry.values[1].value
    if not isinstance(value, str):
        raise TypeError(f"expected string value for option `{key}`")

    if key == "insert_entry":
        try:
            pattern = re.compile(value)
        except re.error as err:
            raise TypeError(
                f"Should be a regular expression: '{value}'.",
            ) from err
        opt = InsertEntryOption(
            entry.date,
            pattern,
            entry.meta["filename"],
            entry.meta["lineno"],
        )
        options.insert_entry.append(opt)
    elif key == "collapse_pattern":
        try:
            pattern = re.compile(value)
        except re.error as err:
            raise TypeError(
                f"Should be a regular expression: '{value}'.",
            ) from err
        options.collapse_pattern.append(pattern)
    elif key == "locale":
        try:
            Locale.parse(value)
            options.locale = value
        except UnknownLocaleError as err:
            raise ValueError(f"Unknown locale: '{value}'.") from err
    elif key == "fiscal_year_end":
        fye = parse_fye_string(value)
        if fye is None:
            raise ValueError("Invalid 'fiscal_year_end' option.")
        options.fiscal_year_end = fye
    elif key in STR_OPTS:
        setattr(options, key, value)
    elif key in BOOL_OPTS:
        setattr(options, key, value.lower() == "true")
    elif key in INT_OPTS:
        setattr(options, key, int(value))
    else:  # key in TUPLE_OPTS
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
        except (IndexError, TypeError, ValueError) as err:
            msg = f"Failed to parse fava-option entry: {err!s}"
            errors.append(OptionError(entry.meta, msg, entry))

    return options, errors
