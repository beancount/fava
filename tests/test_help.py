from __future__ import annotations

from importlib.metadata import version

from fava.help import HELP_PAGES
from fava.help import render_help_page


def test_render_help_page() -> None:
    assert render_help_page("not-a-help-page") is None

    for page_slug in HELP_PAGES:
        assert render_help_page(page_slug)

    index = render_help_page("_index")
    assert index is not None
    assert version("beancount") in index

    options = render_help_page("options")
    assert options is not None
    # the headings get ids so that they can be linked to
    assert '<h2 id="default-file">' in options
    # ```beancount code blocks are rendered as read-only editors
    editor = '<pre><textarea is="beancount-textarea">2016-06-14 custom'
    assert editor in options
