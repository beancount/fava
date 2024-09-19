"""Fava - A web interface for Beancount."""

from __future__ import annotations

from contextlib import suppress
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

with suppress(PackageNotFoundError):
    __version__ = version(__name__)

LOCALES = [
    "bg",
    "ca",
    "de",
    "es",
    "fa",
    "fr",
    "nl",
    "pt",
    "pt_BR",
    "ru",
    "sk",
    "sv",
    "uk",
    "zh",
    "zh_Hant_TW",
]
