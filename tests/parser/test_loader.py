# pylint: disable=missing-docstring

from beancount.core.display_context import Precision

from fava.parser.loader import load_file
from ..conftest import EXAMPLE_FILE


def test_same_entries():
    entries1, errors1, options1 = load_file(EXAMPLE_FILE)
    entries2, errors2, options2 = load_file(EXAMPLE_FILE, False)
    assert errors1 == errors2
    for key, value in options1.items():
        if key != "dcontext":
            assert value == options2[key]
        else:
            ccs1 = options1[key].ccontexts
            ccs2 = options2[key].ccontexts
            for key_ in ccs2:
                mc1 = ccs1[key_].get_fractional(Precision.MOST_COMMON)
                mc2 = ccs2[key_].get_fractional(Precision.MOST_COMMON)
                assert mc1 == mc2, "Display context mismatch: {}".format(key_)

    for left, right in zip(entries1, entries2):
        assert left == right
