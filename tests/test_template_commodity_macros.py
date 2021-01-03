# pylint: disable=missing-docstring
from beancount.core.data import Transaction
from flask import g
from flask import get_template_attribute


COMMODITY_MACROS_PATH = "macros/_commodity_macros.html"


def test_render_currency(app, example_ledger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            COMMODITY_MACROS_PATH, "render_currency"
        )
        assert "US Dollar" in macro(example_ledger, "USD")


def test_render_amount(app, example_ledger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(COMMODITY_MACROS_PATH, "render_amount")
        g.ledger = example_ledger
        transaction = example_ledger.all_entries_by_type[Transaction][0]
        amount = transaction.postings[0].units
        assert "US Dollar" in macro(example_ledger, amount)
