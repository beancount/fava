"""Some small utility functions."""

import functools
import itertools
import logging
import os
import re
import unicodedata
import time

from flask import send_file
from werkzeug.urls import url_quote

BASEPATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def filter_api_changed(record):
    """Filter out LogRecords for requests that poll for changes."""
    return not record.msg.endswith('api/changed/ HTTP/1.1" 200 -')


def setup_logging():
    """Setup logging for Fava."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
    )
    logging.getLogger('werkzeug').addFilter(filter_api_changed)


def resource_path(relative_path):
    """Get absolute path to resource."""
    return os.path.join(BASEPATH, relative_path)


def listify(func):
    """Decorator to make generator function return a list."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable=missing-docstring
        return list(func(*args, **kwargs))
    return wrapper


def timefunc(func):
    """Decorator to time function for debugging."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable=missing-docstring
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('Ran {} in {}'.format(func.__name__, end-start))
        return result
    return wrapper


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    left, right = itertools.tee(iterable)
    next(right, None)
    return zip(left, right)


def slugify(string):
    """Slugify a string.

    Args:
        string: A string.

    Returns:
        A 'slug' of the string suitable for URLs. Retains non-ascii
        characters.

    """
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


def send_as_inline(file_path):
    """Send  a file as an inline, including the original filename."""
    response = send_file(file_path)
    cont_disp = 'inline; filename='
    filename = os.path.basename(file_path)
    try:
        filename = filename.encode('latin-1')
    except UnicodeEncodeError:
        normalized_filename = unicodedata.normalize('NFKD', filename)
        cont_disp += '"{}"; filename*={}'.format(
            normalized_filename.encode('latin-1', 'ignore').decode(),
            "UTF-8''{}".format(url_quote(filename))
        )
    else:
        cont_disp += '"{}"'.format(filename.decode())

    response.headers['Content-Disposition'] = cont_disp
    return response
