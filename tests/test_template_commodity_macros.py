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
        test = '<span title="TEST">TEST</span>'
        assert macro(example_ledger, "TEST") == test


def test_render_amount(app, example_ledger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(COMMODITY_MACROS_PATH, "render_amount")
        res = '<span class="num" title="US Dollar">10.00 USD</span>'
        assert macro(example_ledger, A("10 USD")) == res
        res = '<span class="num"></span>'
        assert macro(example_ledger, None) == res
        res = '<span class="num" title="TEST">10.00 TEST</span>'
        assert macro(example_ledger, A("10 TEST")) == res
