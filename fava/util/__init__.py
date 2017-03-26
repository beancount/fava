"""Some small utility functions."""

import functools
import itertools
import os
import re
import sys
import unicodedata
import time

# get correct path when compiled with PyInstaller
BASEPATH = getattr(sys, '_MEIPASS',
                   os.path.realpath(
                       os.path.join(os.path.dirname(__file__), '..')))


def resource_path(relative_path):
    """Get absolute path to resource, necessary for PyInstaller."""
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
