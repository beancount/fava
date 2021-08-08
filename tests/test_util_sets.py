# pylint: disable=missing-docstring
from fava.util.sets import add_to_set


def test_add_to_set_basic() -> None:
    assert add_to_set(None, "test") == {"test"}
    assert add_to_set({}, "test") == {"test"}
    assert add_to_set({"test"}, "test") == {"test"}


def test_add_to_set_no_mutation() -> None:
    test_set = {"test"}
    assert add_to_set(test_set, "test2") == {"test", "test2"}
    assert test_set == {"test"}
