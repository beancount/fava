"""Fava – A web interface for Beancount."""

import sys
from os import path

from pkg_resources import get_distribution, DistributionNotFound

__version__ = None
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

# if running as pyinstaller bundle, try reading from bundled `version.txt`.
if not __version__ and getattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    with open(path.join(sys._MEIPASS, "fava/version.txt"), "r") as file:
        __version__ = file.read().strip()

LOCALES = [
    "de",
    "es",
    "fa",
    "fr",
    "nl",
    "pt",
    "ru",
    "sk",
    "uk",
    "zh",
    "zh_Hant_TW",
]
LANGUAGES = [locale[:2] for locale in LOCALES]
