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
