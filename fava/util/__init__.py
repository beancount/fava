import os
import re
import sys
import unicodedata

# get correct path when compiled with PyInstaller
BASEPATH = getattr(sys, '_MEIPASS',
                   os.path.realpath(
                       os.path.join(os.path.dirname(__file__), '..')))


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    return os.path.join(BASEPATH, relative_path)


def slugify(string):
    """A version of slugify that retains non-ascii characters."""
    string = unicodedata.normalize('NFKC', string)
    # remove all non-word characters (except '-')
    string = re.sub(r'[^\s\w-]', '', string).strip().lower()
    # replace spaces (or groups of spaces and dashes) with dashes
    string = re.sub(r'[-\s]+', '-', string)
    return string


def simple_wsgi(_, start_response):
    """A simple wsgi app that always returns an empty response."""
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'']


def next_statement_key(keys):
    """Returns the next unused key for `statement` in the supplied array.

    The first try is `statement`, followed by `statement-2`, `statement-3`, etc
    until a free one is found.
    """
    basekey = 'statement'
    if basekey not in keys:
        return basekey
    i = 2
    while '{}-{}'.format(basekey, i) in keys:
        i = i + 1
    return '{}-{}'.format(basekey, i)
