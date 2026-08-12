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
