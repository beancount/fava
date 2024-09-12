"""Build backend that also compiles translations and frontend."""

from __future__ import annotations

import shutil
import subprocess
from itertools import chain
from os import walk
from pathlib import Path
from typing import TYPE_CHECKING

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from setuptools import build_meta
from setuptools.build_meta import get_requires_for_build_editable
from setuptools.build_meta import get_requires_for_build_sdist
from setuptools.build_meta import get_requires_for_build_wheel
from setuptools.build_meta import prepare_metadata_for_build_editable
from setuptools.build_meta import prepare_metadata_for_build_wheel

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

__all__ = [
    "build_editable",
    "build_sdist",
    "build_wheel",
    "get_requires_for_build_editable",
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_editable",
    "prepare_metadata_for_build_wheel",
]


def _frontend_sources() -> Iterable[Path]:
    """List all frontend sources that should trigger a rebuild if changed.

    Yields:
        The files relevant for the frontend build.
    """
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
        msg = "npm is missing"
        raise RuntimeError(msg)

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


def _build_fava() -> None:
    """Run the build steps for Fava."""
    _compile_frontend()
    _compile_translations()


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, str | list[str] | None] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _build_fava()
    return build_meta.build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, str | list[str] | None] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _build_fava()
    return build_meta.build_editable(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, str | list[str] | None] | None = None,
) -> str:
    _build_fava()
    return build_meta.build_sdist(
        sdist_directory,
        config_settings=config_settings,
    )
