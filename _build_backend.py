"""Build backend that also compiles translations and frontend."""

# pylint: disable=wildcard-import,function-redefined,unused-wildcard-import

from __future__ import annotations

import shutil
import subprocess
from itertools import chain
from os import walk
from pathlib import Path
from typing import Iterable

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from setuptools import build_meta as _build_meta_orig
from setuptools.build_meta import *  # noqa: F403


def _frontend_sources() -> Iterable[Path]:
    """List all frontend sources that should trigger a rebuild if changed."""
    yield Path("frontend/package-lock.json")
    yield Path("frontend/build.ts")
    for directory, _dirnames, files in chain(
        walk(Path("frontend/css")),
        walk(Path("frontend/src")),
    ):
        dirpath = Path(directory)
        for file in files:
            yield dirpath / file


def _compile_frontend() -> None:
    """Compile the frontend (if changed or missing)."""
    source_mtime = max(p.stat().st_mtime_ns for p in _frontend_sources())
    app_js = Path("src/fava/static/app.js")
    if app_js.exists() and source_mtime < app_js.stat().st_mtime_ns:
        return

    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is missing")

    # Clean outpute directory before building
    for p in Path("src/fava/static").iterdir():
        if p.name != "favicon.ico":
            p.unlink()

    subprocess.run((npm, "install"), cwd="frontend", check=True)
    Path("frontend/node_modules").touch()
    subprocess.run((npm, "run", "build"), cwd="frontend", check=True)


def _compile_translations() -> None:
    """Compile the translations from .po to .mo (if changed or missing)."""
    for source in Path().glob("src/fava/translations/**/messages.po"):
        target = source.parent / "messages.mo"
        if (
            not target.exists()
            or target.stat().st_mtime_ns < source.stat().st_mtime_ns
        ):
            locale = source.parts[-3]
            catalog = read_po(source.open("rb"), locale)
            write_mo(target.open("wb"), catalog)


def build_sdist(  # type: ignore[no-redef]
    sdist_directory: str,
    config_settings: dict[str, str] | None = None,
) -> str:
    _compile_frontend()
    _compile_translations()
    return _build_meta_orig.build_sdist(
        sdist_directory,
        config_settings=config_settings,
    )
