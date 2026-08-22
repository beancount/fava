"""List of all available help pages."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.renderer import RendererHTML

from fava.core.fava_options import DASHED_OPTION_NAMES
from fava.util import slugify

try:
    from typing import override
except ImportError:  # pragma: no cover
    from typing_extensions import override

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

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
    "features": "Features",
    "filters": "Filtering entries",
    "extensions": "Extensions",
}


class _CustomRenderer(RendererHTML):
    """Some custom help pages rendering logic."""

    @override
    def code_inline(
        self,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        """Link `fava-option` references to their options help page heading."""
        rendered = super().code_inline(tokens, idx, options, env)
        name = tokens[idx].content
        if name not in DASHED_OPTION_NAMES:
            return rendered
        return f'<a href="./options#{name}">{rendered}</a>'

    def heading_open(
        self,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        """Add an id to all headings so that they can be linked to."""
        seen: set[str] = env.setdefault("heading_ids", set())
        slug = slugify(tokens[idx + 1].content)
        if slug in seen:  # pragma: no cover
            msg = f"Duplicate heading {slug}"
            raise ValueError(msg)
        seen.add(slug)
        tokens[idx].attrSet("id", slug)
        return self.renderToken(tokens, idx, options, env)

    @override
    def fence(
        self,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        """Render ```beancount code blocks as read-only Beancount editors."""
        token = tokens[idx]
        if token.info.strip() != "beancount":
            return super().fence(tokens, idx, options, env)
        source = escapeHtml(token.content.rstrip("\n"))
        return (
            f'<pre><textarea is="beancount-textarea">{source}'
            "</textarea></pre>\n"
        )


_MD = MarkdownIt("commonmark", renderer_cls=_CustomRenderer).enable("table")


def render_help_page(page_slug: str) -> str | None:
    """Render the HTML for a help page."""
    if page_slug not in HELP_PAGES:
        return None

    help_path = Path(__file__).parent / (page_slug + ".md")
    contents = help_path.read_text(encoding="utf-8")
    html: str = _MD.render(contents)
    if page_slug == "_index":
        html = html.replace("BEANCOUNT_VERSION", version("beancount"))
        html = html.replace("FAVA_VERSION", version("fava"))
    return html
