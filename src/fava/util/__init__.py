"""Some small utility functions."""

from __future__ import annotations

import gettext
import logging
import re
import time
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING
from unicodedata import normalize
from urllib.parse import quote

from flask import abort
from flask import send_file

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from collections.abc import Mapping
    from typing import Any
    from typing import Callable
    from typing import ParamSpec
    from typing import TypeVar
    from wsgiref.types import StartResponse
    from wsgiref.types import WSGIEnvironment

    from babel import Locale
    from flask.wrappers import Response


def filter_api_changed(record: logging.LogRecord) -> bool:  # pragma: no cover
    """Filter out LogRecords for requests that poll for changes."""
    return "/api/changed HTTP" not in record.getMessage()


def setup_logging() -> None:
    """Set up logging for Fava."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("werkzeug").addFilter(filter_api_changed)


def get_translations(locale: Locale) -> str | None:
    """Check whether Fava has translations for the locale.

    Args:
        locale: The locale to search for

    Returns:
        The path to the found translations or None if none matched.
    """
    translations_dir = Path(__file__).parent.parent / "translations"
    return gettext.find("messages", str(translations_dir), [str(locale)])


if TYPE_CHECKING:  # pragma: no cover
    Item = TypeVar("Item")
    P = ParamSpec("P")
    T = TypeVar("T")


def listify(func: Callable[P, Iterable[Item]]) -> Callable[P, list[Item]]:
    """Make generator function return a list (decorator)."""

    @wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> list[Item]:
        return list(func(*args, **kwargs))

    return _wrapper


def timefunc(
    func: Callable[P, T],
) -> Callable[P, T]:  # pragma: no cover - only used for debugging so far
    """Time function for debugging (decorator)."""

    @wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Ran {func.__name__} in {end - start}")  # noqa: T201
        return result

    return _wrapper


def next_key(basekey: str, keys: Mapping[str, Any]) -> str:
    """Return the next unused key for basekey in the supplied dictionary.

    The first try is `basekey`, followed by `basekey-2`, `basekey-3`, etc
    until a free one is found.
    """
    if basekey not in keys:
        return basekey
    i = 2
    while f"{basekey}-{i}" in keys:
        i += 1
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
    return re.sub(r"[-\s]+", "-", string)


def simple_wsgi(
    _: WSGIEnvironment,
    start_response: StartResponse,
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
    base = Path(filename).name
    cont_disp = f"inline; filename*=UTF-8''{quote(base)}"
    response.headers["Content-Disposition"] = cont_disp
    return response
