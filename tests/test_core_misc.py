# pylint: disable=missing-docstring
import datetime

from beancount.loader import load_string

from fava.core.misc import sidebar_links
from fava.core.misc import upcoming_events


def test_sidebar_links(load_doc):
    """
    2016-01-01 custom "fava-sidebar-link" "title" "link"
    2016-01-02 custom "fava-sidebar-link" "titl1" "lin1"
    """
    entries, _, _ = load_doc
    assert sidebar_links(entries) == [("title", "link"), ("titl1", "lin1")]


def test_upcoming_events():
    entries, _, _ = load_string(
        f'{datetime.date.today()} event "some_event" "test"\n'
        '2012-12-12 event "test" "test"'
    )
    assert len(upcoming_events(entries, 1)) == 1
