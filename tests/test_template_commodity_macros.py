# pylint: disable=missing-docstring
from beancount.core.amount import A
from flask import get_template_attribute


COMMODITY_MACROS_PATH = "macros/_commodity_macros.html"


def test_render_currency(app, example_ledger) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            COMMODITY_MACROS_PATH, "render_currency"
        )
        assert "US Dollar" in macro(example_ledger, "USD")


def test_render_amount(app, example_ledger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(COMMODITY_MACROS_PATH, "render_amount")
        amount = A("10 USD")
        assert "US Dollar" in macro(example_ledger, amount)
