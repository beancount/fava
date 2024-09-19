#!/usr/bin/env python3
"""Various utilities."""

from __future__ import annotations

import json
from os import environ
from pathlib import Path
from typing import Iterable

import requests
from beancount.query import query_env
from beancount.query import query_parser
from click import echo
from click import group
from click import UsageError

from fava import LOCALES

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

    target_env = query_env.TargetsEnvironment()
    data = {
        "columns": sorted(set(_env_to_list(target_env.columns))),
        "functions": sorted(set(_env_to_list(target_env.functions))),
        "keywords": sorted({kw.lower() for kw in query_parser.Lexer.keywords}),
    }
    path = BASE_PATH / "frontend" / "src" / "codemirror" / "bql-grammar.ts"
    path.write_text("export default " + json.dumps(data))


class MissingPoeditorTokenError(UsageError):
    def __init__(self) -> None:
        super().__init__(
            "The POEDITOR_TOKEN environment variable needs to be set."
        )


@cli.command()
def download_translations() -> None:
    """Fetch updated translations from POEditor.com."""
    token = environ.get("POEDITOR_TOKEN")
    if not token:
        raise MissingPoeditorTokenError
    for language in LOCALES:
        download_from_poeditor(language, token)


@cli.command()
def upload_translations() -> None:
    """Upload .pot message catalog to POEditor.com."""
    token = environ.get("POEDITOR_TOKEN")
    if not token:
        raise MissingPoeditorTokenError
    path = FAVA_PATH / "translations" / "messages.pot"
    echo(f"Uploading message catalog: {path}")
    data = {
        "api_token": token,
        "id": 90283,
        "updating": "terms",
        "sync_terms": 1,
    }
    with path.open("rb") as file:
        files = {"file": file}
        request = requests.post(
            "https://api.poeditor.com/v2/projects/upload",
            data=data,
            files=files,
            timeout=10,
        )
        echo("Done: " + str(request.json()["result"]["terms"]))


# For these languages, the name on POEDITOR is off.
POEDITOR_LANGUAGE_NAME = {
    "pt_BR": "pt-BR",
    "zh": "zh-CN",
    "zh_Hant_TW": "zh-TW",
}


def download_from_poeditor(language: str, token: str) -> None:
    """Download .po-file from POEditor and save to disk."""
    echo(f'Downloading .po-file for language "{language}"')
    poeditor_name = POEDITOR_LANGUAGE_NAME.get(language, language)
    data = {
        "api_token": token,
        "id": 90283,
        "language": poeditor_name,
        "type": "po",
    }
    request = requests.post(
        "https://api.poeditor.com/v2/projects/export",
        data=data,
        timeout=10,
    )
    url = request.json()["result"]["url"]
    content = requests.get(url, timeout=10).content
    folder = FAVA_PATH / "translations" / language / "LC_MESSAGES"
    if not folder.exists():
        folder.mkdir(parents=True)
    path = folder / "messages.po"
    path.write_bytes(content)
    echo(f'Downloaded to "{path}"')


if __name__ == "__main__":
    cli()
