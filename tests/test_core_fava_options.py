# pylint: disable=missing-docstring
from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

from fava.core.fava_options import InsertEntryOption
from fava.core.fava_options import parse_options
from fava.util.date import FiscalYearEnd

if TYPE_CHECKING:
    from fava.util.typing import LoaderResult


def test_fava_options(load_doc: LoaderResult) -> None:
    """
    2016-06-14 custom "fava-option" "default-file"
    2016-04-14 custom "fava-option" "show-closed-accounts" "true"
    2016-04-14 custom "fava-option" "journal-show" "transaction open"
    2016-04-14 custom "fava-option" "currency-column" "10"
    2016-04-14 custom "fava-option" "indent" "4"
    2016-04-14 custom "fava-option" "insert-entry" "Ausgaben:Test"
    2016-04-14 custom "fava-option" "invalid"
    2016-04-14 custom "fava-option" "locale" "en"
    2016-04-14 custom "fava-option" "locale" "invalid"
    2016-04-14 custom "fava-option" "collapse-pattern" "Account:Name"
    2016-04-14 custom "fava-option" "collapse_pattern" "(invalid"
    2016-04-14 custom "fava-option" "fiscal-year-end" "01-11"
    """

    entries, _, _ = load_doc
    options, errors = parse_options(entries)  # type: ignore

    assert len(errors) == 3

    assert options.indent == 4
    assert options.insert_entry == [
        InsertEntryOption(
            datetime.date(2016, 4, 14),
            re.compile("Ausgaben:Test"),
            "<string>",
            7,
        )
    ]
    assert options.show_closed_accounts
    assert options.journal_show == ("transaction", "open")
    assert options.currency_column == 10
    assert options.collapse_pattern == [re.compile("Account:Name")]
    assert options.fiscal_year_end == FiscalYearEnd(1, 11)
