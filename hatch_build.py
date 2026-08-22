"""Build hook that compiles the frontend and the translations."""

from __future__ import annotations

import shutil
import subprocess
from itertools import chain
from os import walk
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

try:
    from typing import override
except ImportError:
    from typing_extensions import override

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable


def _frontend_sources(root: Path) -> Iterable[Path]:
    """Iterate frontend sources that should trigger a rebuild if changed."""
    frontend = root / "frontend"
    yield frontend / "package-lock.json"
    yield frontend / "build.ts"
    for directory, _dirnames, files in chain(
        walk(frontend / "css"),
        walk(frontend / "src"),
    ):
        dirpath = Path(directory)
        for file in files:
            yield dirpath / file


def _compile_frontend(root: Path) -> None:
    """Compile the frontend (if changed or missing)."""
    source_mtime = max(p.stat().st_mtime_ns for p in _frontend_sources(root))
    app_js = root / "src/fava/static/app.js"
    if app_js.exists() and source_mtime <= app_js.stat().st_mtime_ns:
        return

    npm = shutil.which("npm")
    if npm is None:
        msg = "npm is missing"
        raise RuntimeError(msg)

    frontend = root / "frontend"
    subprocess.run(
        (npm, "install", "--no-save", "--strict-allow-scripts"),
        cwd=frontend,
        check=True,
    )
    (frontend / "node_modules").touch()
    subprocess.run((npm, "run", "build"), cwd=frontend, check=True)


def _compile_translations(root: Path) -> None:
    """Compile the translations from .po to .mo (if changed or missing)."""
    for source in root.glob("src/fava/translations/**/messages.po"):
        target = source.parent / "messages.mo"
        if (
            not target.exists()
            or target.stat().st_mtime_ns < source.stat().st_mtime_ns
        ):
            locale = source.parts[-3]
            catalog = read_po(source.open("rb"), locale)
            write_mo(target.open("wb"), catalog)


class FavaBuildHook(BuildHookInterface[BuilderConfig]):
    """Build hook to compile the frontend and the translations."""

    @override
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Run the build steps for Fava."""
        root = Path(self.root)
        _compile_frontend(root)
        _compile_translations(root)
