from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

from fava.core.charts import dumps
from fava.core.fava_options import InsertEntryOption
from fava.core.fava_options import parse_options
from fava.util.date import FiscalYearEnd

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Custom


def test_fava_options(load_doc_custom_entries: list[Custom]) -> None:
    """
    2016-06-14 custom "fava-option" "default-file"
    2016-04-14 custom "fava-option" "show-closed-accounts" "true"
    2016-04-14 custom "fava-option" "currency-column" "10"
    2016-04-14 custom "fava-option" "indent" "4"
    2016-04-14 custom "fava-option" "insert-entry" "Ausgaben:Test"
    2016-04-14 custom "fava-option" "invalid"
    2016-04-14 custom "fava-option" "locale" "en"
    2016-04-14 custom "fava-option" "locale" "invalid"
    2016-04-14 custom "fava-option" "collapse-pattern" "Account:Name"
    2016-04-14 custom "fava-option" "collapse_pattern" "(invalid"
    2016-04-14 custom "fava-option" "fiscal-year-end" "01-11"
    2016-04-14 custom "fava-option" "conversion-currencies" "USD EUR HOOLI"
    """

    options, errors = parse_options(load_doc_custom_entries)

    # The options can be encoded to JSON.
    dumps(options)

    assert len(errors) == 3

    assert options.indent == 4
    assert options.insert_entry == [
        InsertEntryOption(
            datetime.date(2016, 4, 14),
            re.compile("Ausgaben:Test"),
            "<string>",
            6,
        ),
    ]
    assert options.show_closed_accounts
    assert options.currency_column == 10
    assert options.collapse_pattern == [re.compile("Account:Name")]
    assert options.fiscal_year_end == FiscalYearEnd(1, 11)
    assert options.conversion_currencies == ("USD", "EUR", "HOOLI")
