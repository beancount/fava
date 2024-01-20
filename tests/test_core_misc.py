from __future__ import annotations

from typing import TYPE_CHECKING

from fava.beans.load import load_string
from fava.core.misc import sidebar_links
from fava.core.misc import upcoming_events
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Custom


def test_sidebar_links(load_doc_custom_entries: list[Custom]) -> None:
    """
    2016-01-01 custom "fava-sidebar-link" "title" "link"
    2016-01-02 custom "fava-sidebar-link" "titl1" "lin1"
    """
    links = sidebar_links(load_doc_custom_entries)
    assert links == [("title", "link"), ("titl1", "lin1")]


def test_upcoming_events() -> None:
    today = local_today()
    entries, _, _ = load_string(
        f'{today} event "some_event" "test"\n2012-12-12 event "test" "test"',
    )
    events = upcoming_events(entries, 1)  # type: ignore[arg-type]
    assert len(events) == 1
