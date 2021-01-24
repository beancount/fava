# pylint: disable=missing-docstring
from flask import get_template_attribute


def test_indicator(app, example_ledger, snapshot) -> None:
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html", "indicator"
        )
        assert macro(example_ledger, "NONEXISTING") == ""
        yellow_status = macro(example_ledger, "Assets:US:BofA:Checking")
        assert "yellow" in yellow_status
        snapshot(yellow_status)
