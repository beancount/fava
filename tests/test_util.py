from fava.util import uniquify


def test_uniquify():
    assert uniquify([1, 1, 2, 3, 3]) == [1, 2, 3]
    assert uniquify([5, 3, 4, 3, 3, 5]) == [5, 3, 4]
