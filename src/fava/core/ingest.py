"""Ingest helper functions."""

from __future__ import annotations

import os
import sys
import traceback
from dataclasses import dataclass
from inspect import signature
from os import altsep
from os import sep
from pathlib import Path
from runpy import run_path
from typing import TYPE_CHECKING

from beangulp import Importer

try:  # pragma: no cover
    from beancount.ingest import cache  # type: ignore[import-untyped]
    from beancount.ingest import extract

    DEFAULT_HOOKS = [extract.find_duplicate_entries]
except ImportError:
    from beangulp import cache

    DEFAULT_HOOKS = []

from fava.beans.ingest import BeanImporterProtocol
from fava.core.file import _incomplete_sortkey
from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.helpers import FavaAPIError
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence
    from typing import Callable

    from fava.beans.abc import Directive
    from fava.beans.ingest import FileMemo
    from fava.core import FavaLedger

    HookOutput = list[tuple[str, list[Directive]]]
    Hooks = Sequence[Callable[[HookOutput, Sequence[Directive]], HookOutput]]


class IngestError(BeancountError):
    """An error with one of the importers."""


class ImporterMethodCallError(FavaAPIError):
    """Error calling one of the importer methods."""

    def __init__(self) -> None:
        super().__init__(
            f"Error calling method on importer:\n\n{traceback.format_exc()}"
        )


class ImporterExtractError(ImporterMethodCallError):
    """Error calling extract for importer."""


class MissingImporterConfigError(FavaAPIError):
    """Missing import-config option."""

    def __init__(self) -> None:
        super().__init__("Missing import-config option")


class MissingImporterDirsError(FavaAPIError):
    """You need to set at least one imports-dir."""

    def __init__(self) -> None:
        super().__init__("You need to set at least one imports-dir.")


class ImportConfigLoadError(FavaAPIError):
    """Error on loading the import config."""


IGNORE_DIRS = {
    ".cache",
    ".git",
    ".hg",
    ".idea",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
}


def walk_dir(directory: Path) -> Iterable[Path]:
    """Walk through all files in dir.

    Ignores common dot-directories like .git, .cache. .venv, see IGNORE_DIRS.

    Args:
        directory: The directory to start in.

    Yields:
        All full paths under directory, ignoring some directories.
    """
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS)
        root_path = Path(root)
        for filename in sorted(filenames):
            yield root_path / filename


# Keep our own cache to also keep track of file mtimes
_CACHE: dict[Path, tuple[int, FileMemo]] = {}


def get_cached_file(path: Path) -> FileMemo:
    """Get a cached FileMemo.

    This checks the file's mtime before getting it from the Cache.
    In addition to using the beangulp cache.
    """
    mtime = path.stat().st_mtime_ns
    filename = str(path)
    cached = _CACHE.get(path)
    if cached:
        mtime_cached, memo_cached = cached
        if mtime <= mtime_cached:  # pragma: no cover
            return memo_cached
    memo: FileMemo = cache._FileMemo(filename)  # noqa: SLF001
    cache._CACHE[filename] = memo  # noqa: SLF001
    _CACHE[path] = (mtime, memo)
    return memo


@dataclass(frozen=True)
class FileImportInfo:
    """Info about one file/importer combination."""

    importer_name: str
    account: str
    date: datetime.date
    name: str


@dataclass(frozen=True)
class FileImporters:
    """Importers for a file."""

    name: str
    basename: str
    importers: list[FileImportInfo]


def get_name(importer: BeanImporterProtocol | Importer) -> str:
    """Get the name of an importer."""
    try:
        if isinstance(importer, Importer):
            return importer.name
        return importer.name()
    except Exception as err:
        raise ImporterMethodCallError from err


def importer_identify(
    importer: BeanImporterProtocol | Importer, path: Path
) -> bool:
    """Get the name of an importer."""
    try:
        if isinstance(importer, Importer):
            return importer.identify(str(path))
        return importer.identify(get_cached_file(path))
    except Exception as err:
        raise ImporterMethodCallError from err


def file_import_info(
    path: Path,
    importer: BeanImporterProtocol | Importer,
) -> FileImportInfo:
    """Generate info about a file with an importer."""
    filename = str(path)
    try:
        if isinstance(importer, Importer):
            account = importer.account(filename)
            date = importer.date(filename)
            name = importer.filename(filename)
        else:
            file = get_cached_file(path)
            account = importer.file_account(file)
            date = importer.file_date(file)
            name = importer.file_name(file)
    except Exception as err:
        raise ImporterMethodCallError from err

    return FileImportInfo(
        get_name(importer),
        account or "",
        date or local_today(),
        name or Path(filename).name,
    )


# Copied here from beangulp to minimise the imports.
_FILE_TOO_LARGE_THRESHOLD = 8 * 1024 * 1024


def find_imports(
    config: Sequence[BeanImporterProtocol | Importer], directory: Path
) -> Iterable[FileImporters]:
    """Pair files and matching importers.

    Yields:
        For each file in directory, a pair of its filename and the matching
        importers.
    """
    for path in walk_dir(directory):
        stat = path.stat()
        if stat.st_size > _FILE_TOO_LARGE_THRESHOLD:  # pragma: no cover
            continue

        importers = [
            file_import_info(path, importer)
            for importer in config
            if importer_identify(importer, path)
        ]
        yield FileImporters(
            name=str(path), basename=path.name, importers=importers
        )


def extract_from_file(
    importer: BeanImporterProtocol | Importer,
    path: Path,
    existing_entries: Sequence[Directive],
) -> list[Directive]:
    """Import entries from a document.

    Args:
      importer: The importer instance to handle the document.
      path: Filesystem path to the document.
      existing_entries: Existing entries.

    Returns:
      The list of imported entries.
    """
    filename = str(path)
    if isinstance(importer, Importer):
        entries = importer.extract(filename, existing=existing_entries)
    else:
        file = get_cached_file(path)
        entries = (
            importer.extract(file, existing_entries=existing_entries)
            if "existing_entries" in signature(importer.extract).parameters
            else importer.extract(file)
        ) or []

    if hasattr(importer, "sort"):
        importer.sort(entries)
    else:
        entries.sort(key=_incomplete_sortkey)
    if isinstance(importer, Importer):
        importer.deduplicate(entries, existing=existing_entries)
    return entries


def load_import_config(
    module_path: Path,
) -> tuple[Mapping[str, BeanImporterProtocol | Importer], Hooks]:
    """Load the given import config and extract importers and hooks.

    Args:
        module_path: Path to the import config.

    Returns:
        A pair of the importers (by name) and the list of hooks.
    """
    try:
        mod = run_path(str(module_path))
    except Exception as error:
        message = "".join(traceback.format_exception(*sys.exc_info()))
        raise ImportConfigLoadError(message) from error

    if "CONFIG" not in mod:
        msg = "CONFIG is missing"
        raise ImportConfigLoadError(msg)
    if not isinstance(mod["CONFIG"], list):  # pragma: no cover
        msg = "CONFIG is not a list"
        raise ImportConfigLoadError(msg)

    config = mod["CONFIG"]
    hooks = DEFAULT_HOOKS
    if "HOOKS" in mod:  # pragma: no cover
        hooks = mod["HOOKS"]
        if not isinstance(hooks, list) or not all(
            callable(fn) for fn in hooks
        ):
            msg = "HOOKS is not a list of callables"
            raise ImportConfigLoadError(msg)
    importers = {}
    for importer in config:
        if not isinstance(
            importer, (BeanImporterProtocol, Importer)
        ):  # pragma: no cover
            name = importer.__class__.__name__
            msg = (
                f"Importer class '{name}' in '{module_path}' does "
                "not satisfy importer protocol"
            )
            raise ImportConfigLoadError(msg)
        importers[get_name(importer)] = importer
    return importers, hooks


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.importers: Mapping[str, BeanImporterProtocol | Importer] = {}
        self.hooks: Hooks = []
        self.mtime: int | None = None
        self.errors: list[IngestError] = []

    @property
    def module_path(self) -> Path | None:
        """The path to the importer configuration."""
        config_path = self.ledger.fava_options.import_config
        if not config_path:
            return None
        return self.ledger.join_path(config_path)

    def _error(self, msg: str) -> None:
        self.errors.append(
            IngestError(
                {"filename": str(self.module_path), "lineno": 0},
                msg,
                None,
            ),
        )

    def load_file(self) -> None:  # noqa: D102
        self.errors = []
        module_path = self.module_path
        if module_path is None:
            return

        if not module_path.exists():
            self._error("Import config does not exist")
            return

        new_mtime = module_path.stat().st_mtime_ns
        if new_mtime == self.mtime:
            return

        try:
            self.importers, self.hooks = load_import_config(module_path)
            self.mtime = new_mtime
        except ImportConfigLoadError as error:
            msg = f"Error in import config '{module_path}': {error!s}"
            self._error(msg)

    def import_data(self) -> list[FileImporters]:
        """Identify files and importers that can be imported.

        Returns:
            A list of :class:`.FileImportInfo`.
        """
        if not self.importers:
            return []

        importers = list(self.importers.values())

        ret: list[FileImporters] = []
        for directory in self.ledger.fava_options.import_dirs:
            full_path = self.ledger.join_path(directory)
            ret.extend(find_imports(importers, full_path))

        return ret

    def extract(self, filename: str, importer_name: str) -> list[Directive]:
        """Extract entries from filename with the specified importer.

        Args:
            filename: The full path to a file.
            importer_name: The name of an importer that matched the file.

        Returns:
            A list of new imported entries.
        """
        if not self.module_path:
            raise MissingImporterConfigError

        # reload (if changed)
        self.load_file()

        try:
            path = Path(filename)
            new_entries = extract_from_file(
                self.importers[importer_name],
                path,
                existing_entries=self.ledger.all_entries,
            )
        except Exception as exc:
            raise ImporterExtractError from exc

        new_entries_list = [(filename, new_entries)]
        for hook_fn in self.hooks:
            new_entries_list = hook_fn(
                new_entries_list,
                self.ledger.all_entries,
            )

        return new_entries_list[0][1]


def filepath_in_primary_imports_folder(
    filename: str,
    ledger: FavaLedger,
) -> Path:
    """File path for a document to upload to the primary import folder.

    Args:
        filename: The filename of the document.
        ledger: The FavaLedger.

    Returns:
        The path that the document should be saved at.
    """
    primary_imports_folder = next(iter(ledger.fava_options.import_dirs), None)
    if primary_imports_folder is None:
        raise MissingImporterDirsError

    for separator in sep, altsep:
        if separator:
            filename = filename.replace(separator, " ")

    return ledger.join_path(primary_imports_folder, filename)
