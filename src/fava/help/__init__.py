"""List of all available help pages."""

from __future__ import annotations

from pathlib import Path

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


def render_help_page(page_slug: str) -> str | None:
    """Render the HTML for a help page."""
    if page_slug not in HELP_PAGES:
        return None

    from importlib.metadata import version  # noqa: PLC0415

    from markdown2 import markdown  # noqa: PLC0415

    help_path = Path(__file__).parent / (page_slug + ".md")
    contents = help_path.read_text(encoding="utf-8")
    html: str = markdown(
        contents,
        extras=["fenced-code-blocks", "tables", "header-ids"],
    )
    if page_slug == "_index":
        html = html.replace("BEANCOUNT_VERSION", version("beancount"))
        html = html.replace("FAVA_VERSION", version("fava"))
    return html
