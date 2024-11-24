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
from pathlib import Path
from typing import TYPE_CHECKING

from babel.core import Locale
from babel.core import UnknownLocaleError

from fava.beans.funcs import get_position
from fava.helpers import BeancountError
from fava.util import get_translations
from fava.util.date import END_OF_YEAR
from fava.util.date import parse_fye_string

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Sequence
    from re import Pattern

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


class MissingOptionError(ValueError):  # noqa: D101
    def __init__(self) -> None:
        super().__init__("Custom entry is missing option name.")


class UnknownOptionError(ValueError):  # noqa: D101
    def __init__(self, key: str) -> None:
        super().__init__(f"Unknown option `{key}`")


class NotARegularExpressionError(TypeError):  # noqa: D101
    def __init__(self, value: str) -> None:
        super().__init__(f"Should be a regular expression: '{value}'.")


class NotAStringOptionError(TypeError):  # noqa: D101
    def __init__(self, key: str) -> None:
        super().__init__(f"Expected string value for option `{key}`")


class UnknownLocaleOptionError(ValueError):  # noqa: D101
    def __init__(self, value: str) -> None:
        super().__init__(f"Unknown locale: '{value}'.")


class UnsupportedLanguageOptionError(ValueError):  # noqa: D101
    def __init__(self, value: str) -> None:
        super().__init__(f"Fava has no translations for: '{value}'.")


class InvalidFiscalYearEndOptionError(ValueError):  # noqa: D101
    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid 'fiscal_year_end' option: '{value}'.")


@dataclass
class FavaOptions:
    """Options for Fava that can be set in the Beancount file."""

    account_journal_include_children: bool = True
    auto_reload: bool = False
    collapse_pattern: Sequence[Pattern[str]] = field(default_factory=list)
    conversion_currencies: tuple[str, ...] = ()
    currency_column: int = 61
    default_file: str | None = None
    default_page: str = "income_statement/"
    fiscal_year_end: FiscalYearEnd = END_OF_YEAR
    import_config: str | None = None
    import_dirs: tuple[str, ...] = ()
    indent: int = 2
    insert_entry: Sequence[InsertEntryOption] = field(default_factory=list)
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

    def set_collapse_pattern(self, value: str) -> None:
        """Set the collapse_pattern option."""
        try:
            pattern = re.compile(value)
        except re.error as err:
            raise NotARegularExpressionError(value) from err
        # It's typed as Sequence so that it's not externally mutated
        self.collapse_pattern.append(pattern)  # type: ignore[attr-defined]

    def set_default_file(self, value: str, filename: str) -> None:
        """Set the default_file option."""
        self.default_file = str(Path(value).absolute()) if value else filename

    def set_fiscal_year_end(self, value: str) -> None:
        """Set the fiscal_year_end option."""
        fye = parse_fye_string(value)
        if fye is None:
            raise InvalidFiscalYearEndOptionError(value)
        self.fiscal_year_end = fye

    def set_insert_entry(
        self, value: str, date: datetime.date, filename: str, lineno: int
    ) -> None:
        """Set the insert_entry option."""
        try:
            pattern = re.compile(value)
        except re.error as err:
            raise NotARegularExpressionError(value) from err
        opt = InsertEntryOption(date, pattern, filename, lineno)
        # It's typed as Sequence so that it's not externally mutated
        self.insert_entry.append(opt)  # type: ignore[attr-defined]

    def set_language(self, value: str) -> None:
        """Set the locale option."""
        try:
            locale = Locale.parse(value)
            if (
                not locale.language == "en"
                and get_translations(locale) is None
            ):
                raise UnsupportedLanguageOptionError(value)
            self.language = value
        except UnknownLocaleError as err:
            raise UnknownLocaleOptionError(value) from err

    def set_locale(self, value: str) -> None:
        """Set the locale option."""
        try:
            Locale.parse(value)
            self.locale = value
        except UnknownLocaleError as err:
            raise UnknownLocaleOptionError(value) from err


_fields = fields(FavaOptions)
All_OPTS = {f.name for f in _fields}
BOOL_OPTS = {f.name for f in _fields if str(f.type) == "bool"}
INT_OPTS = {f.name for f in _fields if str(f.type) == "int"}
TUPLE_OPTS = {f.name for f in _fields if f.type.startswith("tuple[str,")}
STR_OPTS = {f.name for f in _fields if f.type.startswith("str")}


def parse_option_custom_entry(entry: Custom, options: FavaOptions) -> None:
    """Parse a single custom fava-option entry and set option accordingly."""
    key = str(entry.values[0].value).replace("-", "_")
    if key not in All_OPTS:
        raise UnknownOptionError(key)

    value = entry.values[1].value if len(entry.values) > 1 else ""
    if not isinstance(value, str):
        raise NotAStringOptionError(key)
    filename, lineno = get_position(entry)

    if key == "collapse_pattern":
        options.set_collapse_pattern(value)
    elif key == "default_file":
        options.set_default_file(value, filename)
    elif key == "fiscal_year_end":
        options.set_fiscal_year_end(value)
    elif key == "insert_entry":
        options.set_insert_entry(value, entry.date, filename, lineno)
    elif key == "language":
        options.set_language(value)
    elif key == "locale":
        options.set_locale(value)
    elif key in STR_OPTS:
        setattr(options, key, value)
    elif key in BOOL_OPTS:
        setattr(options, key, value.lower() == "true")
    elif key in INT_OPTS:
        setattr(options, key, int(value))
    else:  # key in TUPLE_OPTS
        setattr(options, key, tuple(value.strip().split(" ")))


def parse_options(
    custom_entries: Sequence[Custom],
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
            if not entry.values:
                raise MissingOptionError
            parse_option_custom_entry(entry, options)
        except (IndexError, TypeError, ValueError) as err:
            msg = f"Failed to parse fava-option entry: {err!s}"
            errors.append(OptionError(entry.meta, msg, entry))

    return options, errors
