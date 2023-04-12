"""Fava - A web interface for Beancount."""
from __future__ import annotations

from contextlib import suppress
from sys import version_info

if version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata  # type: ignore[import,no-redef]

with suppress(importlib_metadata.PackageNotFoundError):
    __version__ = importlib_metadata.version(__name__)

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
