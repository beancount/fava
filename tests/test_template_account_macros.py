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


def test_balance_directive(app, example_ledger) -> None:
    bal = "2021-01-24 balance Assets:US:BofA:Checking              1632.79 USD"
    with app.test_request_context(""):
        macro = get_template_attribute(
            "macros/_account_macros.html", "balance_directive"
        )
        assert macro(example_ledger, "NONEXISTING") == ""
        assert macro(example_ledger, "Assets:US:BofA:Checking") == f"{bal}\n"


def test_account_name(app, example_ledger) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            "macros/_account_macros.html", "account_name"
        )
        assert (
            macro(example_ledger, "NONEXISTING")
            == '<a href="/long-example/account/NONEXISTING/"'
            ' class="account">NONEXISTING</a>\n'
        )
        assert (
            macro(example_ledger, "Assets:US:BofA:Checking")
            == '<a href="/long-example/account/Assets:US:BofA:Checking/"'
            ' class="account">Assets:US:BofA:Checking</a>\n'
        )
