"""List of all available help pages."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.renderer import RendererHTML

from fava.util import slugify

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from markdown_it.rules_core import StateCore
    from markdown_it.token import Token
    from markdown_it.utils import EnvType
    from markdown_it.utils import OptionsDict

HELP_PAGES = {
    "_index": "Index",
    "budgets": "Budgets",
    "conversion": "Conversion",
    "import": "Import",
    "options": "Options",
    "beancount_syntax": "Beancount Syntax",
    "features": "Fava's features",
    "filters": "Filtering entries",
    "extensions": "Extensions",
}


def _add_heading_ids(state: StateCore) -> None:
    """Add an id to all headings so that they can be linked to."""
    seen = set()
    for index, token in enumerate(state.tokens):
        if token.type == "heading_open":
            slug = slugify(state.tokens[index + 1].content)
            if slug in seen:  # pragma: no cover
                msg = f"Duplicate heading {slug}"
                raise ValueError(msg)
            seen.add(slug)
            token.attrSet("id", slug)


def _render_fence(
    self: RendererHTML,
    tokens: Sequence[Token],
    index: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    """Render ```beancount code blocks as read-only Beancount editors."""
    token = tokens[index]
    if token.info.strip() != "beancount":
        return RendererHTML.fence(self, tokens, index, options, env)
    source = escapeHtml(token.content.rstrip("\n"))
    return (
        f'<pre><textarea is="beancount-textarea">{source}</textarea></pre>\n'
    )


def render_help_page(page_slug: str) -> str | None:
    """Render the HTML for a help page."""
    if page_slug not in HELP_PAGES:
        return None

    md = MarkdownIt("commonmark").enable("table")
    md.core.ruler.push("heading_ids", _add_heading_ids)
    md.add_render_rule("fence", _render_fence)

    help_path = Path(__file__).parent / (page_slug + ".md")
    contents = help_path.read_text(encoding="utf-8")
    html: str = md.render(contents)
    if page_slug == "_index":
        html = html.replace("BEANCOUNT_VERSION", version("beancount"))
        html = html.replace("FAVA_VERSION", version("fava"))
    return html
