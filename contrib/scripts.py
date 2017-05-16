#!/usr/bin/env python3
import os

import click
import requests

BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '../fava'))
LANGUAGES = ['de', 'es', 'fr', 'nl', 'pt', 'ru', 'zh-CN']


@click.group()
def cli():
    """Various utilities."""
    pass


@cli.command()
def download_translations():
    """Fetch updated translations from POEditor.com."""
    token = os.environ.get('POEDITOR_TOKEN')
    if not token:
        raise click.UsageError(
            'The POEDITOR_TOKEN environment variable needs to be set.')
    for language in LANGUAGES:
        download_from_poeditor(language, 'po', token)
        download_from_poeditor(language, 'mo', token)


@cli.command()
def upload_translations():
    """Upload .pot message catalog to POEditor.com."""
    token = os.environ.get('POEDITOR_TOKEN')
    if not token:
        raise click.UsageError(
            'The POEDITOR_TOKEN environment variable needs to be set.')
    path = os.path.join(
        BASE_PATH,
        f'translations/messages.pot')
    click.echo(f'Uploading message catalog: {path}')
    data = {
        'api_token': token,
        'id': 90283,
        'updating': 'terms',
        'sync_terms': 1,
    }
    files = {
        'file': open(path, 'rb'),
    }
    request = requests.post(
        'https://api.poeditor.com/v2/projects/upload', data=data, files=files)
    click.echo('Done: ' + str(request.json()['result']['terms']))


def download_from_poeditor(language, format_, token):
    """Download .{po,mo}-file from POEditor and save to disk."""
    click.echo(f'Downloading .{format_}-file for language "{language}"')
    language_short = language[:2]
    data = {
        'api_token': token,
        'id': 90283,
        'language': language,
        'type': format_,
    }
    request = requests.post(
        'https://api.poeditor.com/v2/projects/export', data=data)
    url = request.json()['result']['url']
    content = requests.get(url).content
    path = os.path.join(
        BASE_PATH,
        f'translations/{language_short}/LC_MESSAGES/messages.{format_}')
    with open(path, 'wb') as file_:
        file_.write(content)
    click.echo(f'Downloaded to "{path}"')


if __name__ == '__main__':
    cli()
