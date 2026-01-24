"""Rustfava - A web interface for rustledger."""

from __future__ import annotations

LOCALES = [
    "bg",
    "ca",
    "de",
    "es",
    "fa",
    "fr",
    "ja",
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


def __getattr__(name: str) -> str:
    if name == "__version__":
        from importlib.metadata import version

        return version("rustfava")
    raise AttributeError(name)
