"""Fava – A web interface for Beancount."""
from __future__ import annotations

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
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
