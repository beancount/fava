#!/usr/bin/env python3
"""Various utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from beancount.parser.options import OPTIONS_DEFAULTS
from beanquery import connect
from beanquery import query_compile
from beanquery.parser.parser import KEYWORDS
from click import group

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

BASE_PATH = Path(__file__).parent.parent
FAVA_PATH = BASE_PATH / "src" / "fava"


@group()
def cli() -> None:
    """Various utilities."""


def _env_to_list(
    attributes: dict[str, str | tuple[str, str]],
) -> Iterable[str]:
    for name in attributes:
        yield name[0] if isinstance(name, tuple) else name


@cli.command()
def generate_bql_grammar_json() -> None:
    """Generate a JSON file with BQL grammar attributes.

    The online code editor needs to have the list of available columns,
    functions, and keywords for syntax highlighting and completion.

    Should be run whenever the BQL changes."""

    tables = connect(
        "beancount:", entries=[], options=OPTIONS_DEFAULTS, errors=[]
    ).tables  # type: ignore[attr-defined]
    columns = {column for table in tables.values() for column in table.columns}
    data = {
        "columns": sorted(columns),
        "functions": sorted(query_compile.FUNCTIONS.keys()),
        "keywords": sorted({kw.lower() for kw in KEYWORDS}),
    }
    path = BASE_PATH / "frontend" / "src" / "codemirror" / "bql-grammar.ts"
    path.write_text("export default " + json.dumps(data, indent="  "))


if __name__ == "__main__":
    cli()
