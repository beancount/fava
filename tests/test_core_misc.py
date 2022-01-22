# pylint: disable=missing-docstring
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from beancount.loader import load_string

from fava.core.misc import sidebar_links
from fava.core.misc import upcoming_events

if TYPE_CHECKING:
    from fava.util.typing import LoaderResult


def test_sidebar_links(load_doc: LoaderResult) -> None:
    """
    2016-01-01 custom "fava-sidebar-link" "title" "link"
    2016-01-02 custom "fava-sidebar-link" "titl1" "lin1"
    """
    entries, _, _ = load_doc
    links = sidebar_links(entries)  # type: ignore
    assert links == [("title", "link"), ("titl1", "lin1")]


def test_upcoming_events() -> None:
    entries, _, _ = load_string(
        f'{datetime.date.today()} event "some_event" "test"\n'
        '2012-12-12 event "test" "test"'
    )
    events = upcoming_events(entries, 1)  # type: ignore
    assert len(events) == 1
