from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest
from flask import get_template_attribute

from fava.beans import create

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask

    from fava.core import FavaLedger


def test_render_amount(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_commodity_macros.html",
            "render_amount",
        )
        res = "<span class='num' title='US Dollar'>10.00 USD</span>"
        assert macro(example_ledger, create.amount("10 USD")) == res
        res = "<span class='num'></span>"
        assert macro(example_ledger, None) == res
        res = "<span class='num' title='TEST'>10.00 TEST</span>"
        assert macro(example_ledger, create.amount("10 TEST")) == res


def test_account_name(app: Flask, example_ledger: FavaLedger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_account_macros.html",
            "account_name",
        )
        assert (
            macro(example_ledger, "NONEXISTING")
            == '<a href="/long-example/account/NONEXISTING/"'
            ' class="account">NONEXISTING</a>'
        )


@pytest.mark.parametrize(
    ("payee", "narration", "title"),
    [
        (
            "Shop",
            "A long description " * 20,
            "Shop • " + "A long description " * 20,
        ),
        (None, "A narration", "A narration"),
        ("Shop", "", "Shop"),
        (None, "", ""),
        (
            "O'Reilly & Sons",
            'A "quoted" <description>',
            "O&#39;Reilly &amp; Sons • A &#34;quoted&#34; &lt;description&gt;",
        ),
    ],
)
def test_journal_transaction_title(
    app: Flask, payee: str | None, narration: str, title: str
) -> None:
    """Expose the full transaction description in a safely escaped tooltip."""
    entry = create.transaction(
        {"filename": "test.beancount", "lineno": 1},
        date(2026, 1, 1),
        "*",
        payee,
        narration,
        postings=[create.posting("Assets:Cash", create.amount("10 USD"))],
    )
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "_journal_table.html", "journal_table_contents"
        )
        result = macro([(0, entry)])
        assert f"<span class='description' title='{title}'>" in result
        assert result.count("class='description' title=") == 1
        assert "<span class='description'><a " in result
