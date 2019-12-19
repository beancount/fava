"""Some small utility functions."""
import functools
import itertools
import logging
import os
import re
import time
import unicodedata

from flask import abort
from flask import send_file
from werkzeug.urls import url_quote

BASEPATH = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))


def filter_api_changed(record):
    """Filter out LogRecords for requests that poll for changes."""
    return not record.msg.endswith('api/changed/ HTTP/1.1" 200 -')


def setup_logging() -> None:
    """Setup logging for Fava."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("werkzeug").addFilter(filter_api_changed)


def resource_path(relative_path):
    """Get absolute path to resource."""
    return os.path.join(BASEPATH, relative_path)


def listify(func):
    """Decorator to make generator function return a list."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))

    return _wrapper


def timefunc(func):
    """Decorator to time function for debugging."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Ran {} in {}".format(func.__name__, end - start))
        return result

    return _wrapper


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
    string = unicodedata.normalize("NFKC", string)
    # remove all non-word characters (except '-')
    string = re.sub(r"[^\s\w-]", "", string).strip().lower()
    # replace spaces (or groups of spaces and dashes) with dashes
    string = re.sub(r"[-\s]+", "-", string)
    return string


def simple_wsgi(_, start_response):
    """A simple wsgi app that always returns an empty response."""
    start_response("200 OK", [("Content-Type", "text/html")])
    return [b""]


def send_file_inline(filename):
    """Send a file inline, including the original filename.

    Ref: http://test.greenbytes.de/tech/tc2231/.
    """
    try:
        response = send_file(filename)
    except FileNotFoundError:
        return abort(404)
    basename = os.path.basename(filename)
    cont_disp = "inline; filename*=UTF-8''{}".format(url_quote(basename))
    response.headers["Content-Disposition"] = cont_disp
    return response
