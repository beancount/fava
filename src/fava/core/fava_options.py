"""Fava's options.

Options for Fava can be specified through Custom entries in the Beancount file.
This module contains a list of possible options, the defaults and the code for
parsing the options.

"""
import copy
import datetime
import re
from typing import Any
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Pattern
from typing import Tuple

from babel.core import Locale  # type: ignore
from babel.core import UnknownLocaleError
from beancount.core.data import Custom

from fava.helpers import BeancountError
from fava.util.date import FiscalYearEnd
from fava.util.date import parse_fye_string
from fava.util.typing import TypedDict


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


FavaOptions = TypedDict(
    "FavaOptions",
    {
        "account-journal-include-children": bool,
        "currency-column": int,
        "collapse-pattern": List[str],
        "auto-reload": bool,
        "default-file": Optional[str],
        "default-page": str,
        "fiscal-year-end": FiscalYearEnd,
        "import-config": Optional[str],
        "import-dirs": List[str],
        "indent": int,
        "insert-entry": List[InsertEntryOption],
        "invert-income-liabilities-equity": bool,
        "journal-show": List[str],
        "journal-show-document": List[str],
        "journal-show-transaction": List[str],
        "language": Optional[str],
        "locale": Optional[str],
        "show-accounts-with-zero-balance": bool,
        "show-accounts-with-zero-transactions": bool,
        "show-closed-accounts": bool,
        "sidebar-show-queries": int,
        "unrealized": str,
        "upcoming-events": int,
        "uptodate-indicator-grey-lookback-days": int,
        "use-external-editor": bool,
    },
)


DEFAULTS: FavaOptions = {
    "account-journal-include-children": True,
    "currency-column": 61,
    "collapse-pattern": [],
    "auto-reload": False,
    "default-file": None,
    "default-page": "income_statement/",
    "fiscal-year-end": FiscalYearEnd(12, 31),
    "import-config": None,
    "import-dirs": [],
    "indent": 2,
    "insert-entry": [],
    "invert-income-liabilities-equity": False,
    "journal-show": [
        "transaction",
        "balance",
        "note",
        "document",
        "custom",
        "budget",
        "query",
    ],
    "journal-show-document": ["discovered", "statement"],
    "journal-show-transaction": ["cleared", "pending"],
    "language": None,
    "locale": None,
    "show-accounts-with-zero-balance": True,
    "show-accounts-with-zero-transactions": True,
    "show-closed-accounts": False,
    "sidebar-show-queries": 5,
    "unrealized": "Unrealized",
    "upcoming-events": 7,
    "uptodate-indicator-grey-lookback-days": 60,
    "use-external-editor": False,
}

BOOL_OPTS = [
    "account-journal-include-children",
    "auto-reload",
    "invert-income-liabilities-equity",
    "show-accounts-with-zero-balance",
    "show-accounts-with-zero-transactions",
    "show-closed-accounts",
    "use-external-editor",
]

INT_OPTS = [
    "currency-column",
    "indent",
    "sidebar-show-queries",
    "upcoming-events",
    "uptodate-indicator-grey-lookback-days",
]

LIST_OPTS = [
    "import-dirs",
    "journal-show",
    "journal-show-document",
    "journal-show-transaction",
]

STR_OPTS = [
    "collapse-pattern",
    "default-page",
    "import-config",
    "language",
    "unrealized",
]

# options that can be specified multiple times
MULTI_OPTS = ["collapse-pattern"]


# pylint: disable=too-many-branches
def parse_options(
    custom_entries: List[Custom],
) -> Tuple[FavaOptions, Iterable[BeancountError]]:
    """Parse custom entries for Fava options.

    The format for option entries is the following::

        2016-04-01 custom "fava-option" "[name]" "[value]"

    Args:
        custom_entries: A list of Custom entries.

    Returns:
        A tuple (options, errors) where options is a dictionary of all options
        to values, and errors contains possible parsing errors.
    """

    options: FavaOptions = copy.deepcopy(DEFAULTS)
    errors = []

    for entry in (e for e in custom_entries if e.type == "fava-option"):
        try:
            key = entry.values[0].value
            assert key in DEFAULTS, f"unknown option `{key}`"

            if key == "default-file":
                options["default-file"] = entry.meta["filename"]
                continue
            if key == "insert-entry":
                opt = InsertEntryOption(
                    entry.date,
                    re.compile(entry.values[1].value),
                    entry.meta["filename"],
                    entry.meta["lineno"],
                )
                options["insert-entry"].append(opt)
                continue

            value = entry.values[1].value
            assert isinstance(
                value, str
            ), f"expected value for option `{key}` to be a string"

            processed_value: Any = None
            if key in STR_OPTS:
                processed_value = value
            elif key == "locale":
                try:
                    Locale.parse(value)
                    processed_value = value
                except UnknownLocaleError:
                    assert False, f"Unknown locale: '{value}'."
            elif key == "fiscal-year-end":
                processed_value = parse_fye_string(value)
                assert processed_value, "Invalid 'fiscal-year-end' option."
            elif key in BOOL_OPTS:
                processed_value = value.lower() == "true"
            elif key in INT_OPTS:
                processed_value = int(value)
            elif key in LIST_OPTS:
                processed_value = str(value).strip().split(" ")

            if processed_value is not None:
                if key in MULTI_OPTS:
                    options[key].append(processed_value)  # type: ignore
                else:
                    options[key] = processed_value  # type: ignore

        except (IndexError, TypeError, AssertionError) as err:
            msg = f"Failed to parse fava-option entry: {str(err)}"
            errors.append(OptionError(entry.meta, msg, entry))

    return options, errors
