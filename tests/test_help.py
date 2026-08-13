from __future__ import annotations

from importlib.metadata import version

from fava.core.fava_options import DASHED_OPTION_NAMES
from fava.help import HELP_PAGES
from fava.help import render_help_page


def test_render_help_page() -> None:
    assert render_help_page("not-a-help-page") is None

    for page_slug in HELP_PAGES:
        assert render_help_page(page_slug)

    index = render_help_page("_index")
    assert index
    assert version("beancount") in index

    options = render_help_page("options")
    assert options
    # ```beancount code blocks are rendered as read-only editors
    editor = '<pre><textarea is="beancount-textarea">2016-06-14 custom'
    assert editor in options

    # references to Fava options are turned into links to those headings
    features = render_help_page("features")
    assert features
    assert (
        '<a href="./options#default-file"><code>default-file</code></a>'
        in features
    )


def test_render_help_page_option_links_have_targets() -> None:
    """All the options have a heading on the options page."""
    options = render_help_page("options")
    assert options
    for name in DASHED_OPTION_NAMES:
        assert f'<h2 id="{name}">{name}</h2>' in options
