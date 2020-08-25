"""Some small utility functions."""
import functools
import itertools
import logging
import os
import re
import time
import unicodedata
from pathlib import Path
from typing import Any
from typing import Dict

from flask import abort
from flask import send_file
from werkzeug.urls import url_quote

BASEPATH = Path(__file__).parent.parent


def filter_api_changed(record):
    """Filter out LogRecords for requests that poll for changes."""
    return "/api/changed HTTP" not in record.msg


def setup_logging() -> None:
    """Setup logging for Fava."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("werkzeug").addFilter(filter_api_changed)


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource."""
    return BASEPATH / relative_path


def listify(func):
    """Decorator to make generator function return a list."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))

    return _wrapper


def timefunc(func):  # pragma: no cover - only used for debugging so far
    """Decorator to time function for debugging."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Ran {func.__name__} in {end - start}")
        return result

    return _wrapper


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    left, right = itertools.tee(iterable)
    next(right, None)
    return zip(left, right)


def next_key(basekey: str, keys: Dict[str, Any]) -> str:
    """Returns the next unused key for basekey in the supplied dictionary.

    The first try is `basekey`, followed by `basekey-2`, `basekey-3`, etc
    until a free one is found.
    """
    if basekey not in keys:
        return basekey
    i = 2
    while f"{basekey}-{i}" in keys:
        i = i + 1
    return f"{basekey}-{i}"


def slugify(string: str) -> str:
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
    cont_disp = f"inline; filename*=UTF-8''{url_quote(basename)}"
    response.headers["Content-Disposition"] = cont_disp
    return response
