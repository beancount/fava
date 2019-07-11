#!/usr/bin/env python3
"""Various utilities."""

import json
import os

import click
import requests
from beancount.query import query_env
from beancount.query import query_parser

from fava import LOCALES

BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../fava")
)


@click.group()
def cli():
    """Various utilities."""


def _env_to_list(attributes):
    for name in attributes.keys():
        if isinstance(name, tuple):
            name = name[0]
        yield name


@cli.command()
def generate_bql_grammar_json():
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
    path = os.path.join(
        os.path.dirname(__file__),
        "../fava/static/javascript/codemirror/bql-grammar.json",
    )
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)


@cli.command()
def download_translations():
    """Fetch updated translations from POEditor.com."""
    token = os.environ.get("POEDITOR_TOKEN")
    if not token:
        raise click.UsageError(
            "The POEDITOR_TOKEN environment variable needs to be set."
        )
    for language in LOCALES:
        download_from_poeditor(language, token)


@cli.command()
def upload_translations():
    """Upload .pot message catalog to POEditor.com."""
    token = os.environ.get("POEDITOR_TOKEN")
    if not token:
        raise click.UsageError(
            "The POEDITOR_TOKEN environment variable needs to be set."
        )
    path = os.path.join(BASE_PATH, f"translations/messages.pot")
    click.echo(f"Uploading message catalog: {path}")
    data = {
        "api_token": token,
        "id": 90283,
        "updating": "terms",
        # "sync_terms": 1,
    }
    files = {"file": open(path, "rb")}
    request = requests.post(
        "https://api.poeditor.com/v2/projects/upload", data=data, files=files
    )
    click.echo("Done: " + str(request.json()["result"]["terms"]))


# For these languages, the name on POEDITOR is off.
POEDITOR_LANGUAGE_NAME = {"zh": "zh-CN", "zh_Hant_TW": "zh-TW"}


def download_from_poeditor(language, token):
    """Download .po-file from POEditor and save to disk."""
    click.echo(f'Downloading .po-file for language "{language}"')
    poeditor_name = POEDITOR_LANGUAGE_NAME.get(language, language)
    data = {
        "api_token": token,
        "id": 90283,
        "language": poeditor_name,
        "type": "po",
    }
    request = requests.post(
        "https://api.poeditor.com/v2/projects/export", data=data
    )
    url = request.json()["result"]["url"]
    content = requests.get(url).content
    folder = os.path.join(BASE_PATH, "translations", language, "LC_MESSAGES")
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, f"messages.po")
    with open(path, "wb") as file_:
        file_.write(content)
    click.echo(f'Downloaded to "{path}"')


if __name__ == "__main__":
    cli()
