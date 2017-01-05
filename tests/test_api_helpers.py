import pytest

from fava.core import FavaAPIException
from fava.core.helpers import entry_at_lineno


def test_entry_at_lineno(load_doc):
    """
    plugin "auto_accounts"

    2016-01-01 * "Test" "Test"
      Equity:Unknown
      Assets:Cash           5000 USD
    """
    entries, _, _ = load_doc
    assert entries[0] == entry_at_lineno(entries, '<string>', 4)

    with pytest.raises(FavaAPIException):
        entry_at_lineno(entries, '<string>', 1)

    with pytest.raises(FavaAPIException):
        entry_at_lineno(entries, 'foo', 4)
