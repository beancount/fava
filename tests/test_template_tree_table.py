# pylint: disable=missing-docstring
from decimal import Decimal

from flask import get_template_attribute

from fava.core.inventory import CounterInventory

TREE_TABLE_PATH = "_tree_table.html"


def test_render_diff_and_number(app, snapshot) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            TREE_TABLE_PATH, "render_diff_and_number"
        )

        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(12)})
            cost = CounterInventory({"EUR": Decimal(10)})
            snapshot(macro(balance, cost, "EUR", invert))
        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(10)})
            cost = CounterInventory({"EUR": Decimal(12)})
            snapshot(macro(balance, cost, "EUR", invert))
