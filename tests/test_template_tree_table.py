# pylint: disable=missing-docstring
from __future__ import annotations

from decimal import Decimal

from flask import Flask
from flask import get_template_attribute

from .conftest import SnapshotFunc
from fava.core.inventory import CounterInventory

TREE_TABLE_PATH = "_tree_table.html"


def test_render_diff_and_number(app: Flask, snapshot: SnapshotFunc) -> None:
    with app.test_request_context("/long-example/"):
        app.preprocess_request()
        macro = get_template_attribute(
            TREE_TABLE_PATH, "render_diff_and_number"
        )

        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(12)})  # type: ignore
            cost = CounterInventory({"EUR": Decimal(10)})  # type: ignore
            snapshot(macro(balance, cost, "EUR", invert))
        for invert in [False, True]:
            balance = CounterInventory({"EUR": Decimal(10)})  # type: ignore
            cost = CounterInventory({"EUR": Decimal(12)})  # type: ignore
            snapshot(macro(balance, cost, "EUR", invert))
