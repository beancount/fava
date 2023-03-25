"""Fava - A web interface for Beancount."""
from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import PackageNotFoundError  # type: ignore
    from importlib_metadata import version  # type: ignore

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass

LOCALES = [
    "bg",
    "ca",
    "de",
    "es",
    "fa",
    "fr",
    "nl",
    "pt",
    "ru",
    "sk",
    "sv",
    "uk",
    "zh",
    "zh_Hant_TW",
]
LANGUAGES = [locale[:2] for locale in LOCALES]
