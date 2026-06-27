"""Ingest helper functions."""

from __future__ import annotations

import datetime
import os
import runpy
import sys
import traceback
from collections.abc import Sequence
from dataclasses import dataclass
from functools import wraps
from inspect import get_annotations
from os import altsep
from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

from beangulp.importer import Importer

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.helpers import FavaAPIError
from fava.util import listify
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Mapping
    from typing import Any
    from typing import ParamSpec
    from typing import TypeVar

    from fava.beans.abc import Directive
    from fava.core import FavaLedger

    HookOutput = (
        list[tuple[str, list[Directive], str, Importer]]
        | list[tuple[str, list[Directive]]]
    )
    Hooks = Sequence[Callable[[HookOutput, Sequence[Directive]], HookOutput]]

    P = ParamSpec("P")
    T = TypeVar("T")


class IngestError(BeancountError):
    """An error with one of the importers."""


class ImporterMethodCallError(FavaAPIError):
    """Error calling one of the importer methods."""

    def __init__(self) -> None:
        super().__init__(
            f"Error calling method on importer:\n\n{traceback.format_exc()}"
        )


class ImporterInvalidTypeError(FavaAPIError):
    """One of the importer methods returned an unexpected type."""

    def __init__(self, attr: str, expected: type[Any], actual: Any) -> None:
        super().__init__(
            f"Got unexpected type from importer as {attr}:"
            f" expected {expected!s}, got {type(actual)!s}:"
        )


class ImporterExtractError(ImporterMethodCallError):
    """Error calling extract for importer."""


class MissingImporterConfigError(FavaAPIError):
    """Missing import-config option."""


class MissingImporterDirsError(FavaAPIError):
    """You need to set at least one imports-dir."""


class ImportConfigLoadError(FavaAPIError):
    """Error on loading the import config."""


class ImportConfigRunpyError(ImportConfigLoadError):
    """Error running the import config."""

    def __init__(self) -> None:
        super().__init__("".join(traceback.format_exception(*sys.exc_info())))


class ImportConfigMissingConfigError(ImportConfigLoadError):
    """CONFIG is missing."""


class ImportConfigConfigNotASequenceError(ImportConfigLoadError):
    """CONFIG is not a Sequence."""


class ImportConfigHooksNotASequenceCallablesError(ImportConfigLoadError):
    """HOOKS is not a Sequence of callables."""


class ImportConfigInvalidImporterError(ImportConfigLoadError):
    """Invalid importer (not a subclass of Importer)."""

    def __init__(self, importer: Any) -> None:
        name = importer.__class__.__name__
        super().__init__(
            f"Importer class '{name}' does not satisfy Importer protocol"
        )


class ImportConfigDuplicateImporterError(ImportConfigLoadError):
    """Duplicate importer (by name)."""

    def __init__(self, importer: WrappedImporter) -> None:
        super().__init__(f"Duplicate importer name found: {importer.name}")


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


def _catch_any(func: Callable[P, T]) -> Callable[P, T]:
    """Helper to catch any exception that might be raised by the importer."""

    @wraps(func)
    def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
        try:
            return func(*args, **kwds)
        except ImporterInvalidTypeError:
            raise
        except Exception as err:
            raise ImporterMethodCallError from err

    return wrapper


def _assert_type(attr: str, value: T, type_: type[T]) -> T:
    """Helper to validate types return by importer methods."""
    if not isinstance(value, type_):
        raise ImporterInvalidTypeError(attr, type_, value)
    return value


@dataclass(frozen=True)
class WrappedImporter:
    """A wrapper to safely call importer methods."""

    importer: Importer

    @property
    @_catch_any
    def name(self) -> str:
        """Get the name of the importer."""
        importer = self.importer
        name = importer.name
        return _assert_type("name", name, str)

    @_catch_any
    def identify(self: WrappedImporter, path: Path) -> bool:
        """Whether the importer is matching the file."""
        importer = self.importer
        matches = importer.identify(str(path))
        return _assert_type("identify", matches, bool)

    @_catch_any
    def file_import_info(self, path: Path) -> FileImportInfo:
        """Generate info about a file with an importer."""
        importer = self.importer
        str_path = str(path)
        account = importer.account(str_path)
        date = importer.date(str_path)
        filename = importer.filename(str_path)

        return FileImportInfo(
            self.name,
            _assert_type("account", account or "", str),
            _assert_type("date", date or local_today(), datetime.date),
            _assert_type("filename", filename or path.name, str),
        )


# Copied here from beangulp to minimise the imports.
# Skip files over 8MB
_FILE_TOO_LARGE_THRESHOLD = 8 * 1024 * 1024


def extract_from_file(
    wrapped_importer: WrappedImporter,
    path: Path,
    existing_entries: Sequence[Directive],
) -> list[Directive]:
    """Import entries from a document.

    Args:
      wrapped_importer: The importer instance to handle the document.
      path: Filesystem path to the document.
      existing_entries: Existing entries.

    Returns:
      The list of imported entries.
    """
    filename = str(path)
    importer = wrapped_importer.importer
    entries = importer.extract(filename, existing=existing_entries)  # type: ignore[arg-type]
    importer.sort(entries)
    importer.deduplicate(entries, existing=existing_entries)  # type: ignore[arg-type]
    return entries  # type: ignore[return-value]


@dataclass(frozen=True)
class LoadedImportConfig:
    """The import configuration that was successfully loaded."""

    importers: Mapping[str, WrappedImporter]
    hooks: Hooks


def load_import_config(module_path: Path) -> LoadedImportConfig:
    """Load the given import config and extract importers and hooks.

    Args:
        module_path: Path to the import config.

    Returns:
        A pair of the importers (by name) and the list of hooks.
    """
    try:
        mod = runpy.run_path(str(module_path))
    except Exception as error:
        raise ImportConfigRunpyError from error

    config = mod.get("CONFIG")
    if config is None:
        raise ImportConfigMissingConfigError
    if not isinstance(config, Sequence):
        raise ImportConfigConfigNotASequenceError

    hooks = mod.get("HOOKS", ())
    if not isinstance(hooks, Sequence) or not all(
        callable(fn) for fn in hooks
    ):
        raise ImportConfigHooksNotASequenceCallablesError
    importers = {}
    for importer in config:
        if not isinstance(importer, Importer):
            raise ImportConfigInvalidImporterError(importer)
        wrapped_importer = WrappedImporter(importer)
        if wrapped_importer.name in importers:
            raise ImportConfigDuplicateImporterError(wrapped_importer)
        importers[wrapped_importer.name] = wrapped_importer
    return LoadedImportConfig(importers, tuple(hooks))


class IngestModule(FavaModule):
    """Exposes ingest functionality."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.loaded_config: LoadedImportConfig | None = None
        self.mtime: int | None = None
        self.errors: tuple[IngestError, ...] = ()

    @property
    def module_path(self) -> Path | None:
        """The path to the importer configuration."""
        config_path = self.ledger.fava_options.import_config
        return self.ledger.join_path(config_path) if config_path else None

    def _error(self, msg: str) -> tuple[IngestError]:
        return (
            IngestError({"filename": str(self.module_path), "lineno": 0}, msg),
        )

    def load_file(self) -> None:  # noqa: D102
        self.errors = ()
        module_path = self.module_path
        if module_path is None:
            self.loaded_config = None
            return

        if not module_path.exists():
            self.loaded_config = None
            self.errors = self._error("Import config does not exist")
            return

        new_mtime = module_path.stat().st_mtime_ns
        if self.loaded_config and new_mtime == self.mtime:
            return

        try:
            self.loaded_config = load_import_config(module_path)
            self.mtime = new_mtime
        except ImportConfigLoadError as error:
            self.errors = self._error(
                f"Error in import config '{module_path}': {error!s}"
            )

    @listify
    def import_data(self) -> Iterable[FileImporters]:
        """Identify files and importers that can be imported.

        Returns:
            A list of :class:`.FileImportInfo`.
        """
        if not self.loaded_config:
            return

        importers = list(self.loaded_config.importers.values())
        seen = set()

        for directory in self.ledger.fava_options.import_dirs:
            for path in walk_dir(self.ledger.join_path(directory)):
                if path in seen:
                    continue
                seen.add(path)

                if (
                    path.stat().st_size > _FILE_TOO_LARGE_THRESHOLD
                ):  # pragma: no cover
                    continue

                yield FileImporters(
                    name=str(path),
                    basename=path.name,
                    importers=[
                        importer.file_import_info(path)
                        for importer in importers
                        if importer.identify(path)
                    ],
                )

    def extract(self, filename: str, importer_name: str) -> list[Directive]:
        """Extract entries from filename with the specified importer.

        Args:
            filename: The full path to a file.
            importer_name: The name of an importer that matched the file.

        Returns:
            A list of new imported entries.
        """
        if not self.loaded_config:
            raise MissingImporterConfigError

        try:
            path = Path(filename)
            importer = self.loaded_config.importers[importer_name]
            new_entries = extract_from_file(
                importer,
                path,
                existing_entries=self.ledger.all_entries,
            )
        except Exception as exc:
            raise ImporterExtractError from exc

        for hook_fn in self.loaded_config.hooks:
            annotations = get_annotations(hook_fn)
            if any("Importer" in a for a in annotations.values()):
                importer_info = importer.file_import_info(path)
                new_entries_list: HookOutput = [
                    (
                        filename,
                        new_entries,
                        importer_info.account,
                        importer.importer,
                    )
                ]
            else:
                new_entries_list = [(filename, new_entries)]

            new_entries_list = hook_fn(
                new_entries_list,
                self.ledger.all_entries,
            )

            new_entries = new_entries_list[0][1]

        return new_entries


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

    filename = filename.replace(sep, " ")
    if altsep:  # pragma: no cover
        filename = filename.replace(altsep, " ")

    return ledger.join_path(primary_imports_folder, filename)
