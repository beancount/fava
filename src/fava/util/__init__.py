"""Some small utility functions."""
from __future__ import annotations

import logging
import re
import time
from functools import wraps
from itertools import tee
from os.path import basename
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import TYPE_CHECKING
from typing import TypeVar
from unicodedata import normalize

from flask import abort
from flask import send_file
from flask.wrappers import Response
from werkzeug.urls import url_quote

if TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import StartResponse
    from _typeshed.wsgi import WSGIEnvironment


BASEPATH = Path(__file__).parent.parent


def filter_api_changed(record: Any) -> bool:
    """Filter out LogRecords for requests that poll for changes."""
    return "/api/changed HTTP" not in record.getMessage()


def setup_logging() -> None:
    """Set up logging for Fava."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("werkzeug").addFilter(filter_api_changed)


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource."""
    return BASEPATH / relative_path


Item = TypeVar("Item")


def listify(
    func: Callable[..., Generator[Item, None, None]]
) -> Callable[..., list[Item]]:
    """Make generator function return a list (decorator)."""

    @wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> list[Item]:
        return list(func(*args, **kwargs))

    return _wrapper


def timefunc(
    func: Any,
) -> Any:  # pragma: no cover - only used for debugging so far
    """Time function for debugging (decorator)."""

    @wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Ran {func.__name__} in {end - start}")
        return result

    return _wrapper


def pairwise(iterable: Iterable[Item]) -> Iterator[tuple[Item, Item]]:
    """Iterate over consecutive pairs of the given iterable.

    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    left, right = tee(iterable)
    next(right, None)
    return zip(left, right)


def next_key(basekey: str, keys: dict[str, Any]) -> str:
    """Return the next unused key for basekey in the supplied dictionary.

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
    string = normalize("NFKC", string)
    # remove all non-word characters (except '-')
    string = re.sub(r"[^\s\w-]", "", string).strip().lower()
    # replace spaces (or groups of spaces and dashes) with dashes
    string = re.sub(r"[-\s]+", "-", string)
    return string


def simple_wsgi(
    _: WSGIEnvironment, start_response: StartResponse
) -> list[bytes]:
    """Return an empty response (a simple WSGI app)."""
    start_response("200 OK", [("Content-Type", "text/html")])
    return [b""]


def send_file_inline(filename: str) -> Response:
    """Send a file inline, including the original filename.

    Ref: http://test.greenbytes.de/tech/tc2231/.
    """
    try:
        response: Response = send_file(filename)
    except FileNotFoundError:
        return abort(404)
    base = basename(filename)
    cont_disp = f"inline; filename*=UTF-8''{url_quote(base)}"
    response.headers["Content-Disposition"] = cont_disp
    return response
