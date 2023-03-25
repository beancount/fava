# pylint: disable=missing-docstring
from __future__ import annotations

from fava.beans.account import parent


def test_account_parent() -> None:
    assert parent("Assets") is None
    assert parent("Assets:Cash") == "Assets"
    assert parent("Assets:Cash:AA") == "Assets:Cash"
    assert parent("Assets:asdfasdf") == "Assets"
