"""A simple file and folder watcher."""

from __future__ import annotations

import abc
import atexit
import logging
import threading
from itertools import chain
from os import walk
from pathlib import Path
from time import time_ns
from typing import Iterable
from typing import TYPE_CHECKING

from watchfiles import watch

if TYPE_CHECKING:  # pragma: no cover
    import types


log = logging.getLogger(__name__)


class _WatchfilesThread(threading.Thread):
    def __init__(self, paths: list[Path], mtime: int) -> None:
        super().__init__(daemon=True)
        self._stop_event = threading.Event()
        self.paths = paths
        self.mtime = mtime

    def stop(self) -> None:
        """Set the stop event for watchfiles and join the thread."""
        self._stop_event.set()
        self.join()

    def run(self) -> None:
        """Watch for changes."""
        atexit.register(self.stop)

        for changes in watch(*self.paths, stop_event=self._stop_event):
            for _, path in changes:
                try:
                    change_mtime = Path(path).stat().st_mtime_ns
                except FileNotFoundError:
                    change_mtime = time_ns()
                self.mtime = max(change_mtime, self.mtime)
            log.debug("new mtime: %s", self.mtime)


class WatcherBase(abc.ABC):
    """ABC for Fava ledger file watchers."""

    last_checked: int
    """Timestamp of the latest change noticed by the file watcher."""

    last_notified: int
    """Timestamp of the latest change that the watcher was notified of."""

    @abc.abstractmethod
    def update(self, files: Iterable[Path], folders: Iterable[Path]) -> None:
        """Update the folders/files to watch.

        Args:
            files: A list of file paths.
            folders: A list of paths to folders.
        """

    def check(self) -> bool:
        """Check for changes.

        Returns:
            `True` if there was a file change in one of the files or folders,
            `False` otherwise.
        """
        latest_mtime = max(self._get_latest_mtime(), self.last_notified)
        has_higher_mtime = latest_mtime > self.last_checked
        if has_higher_mtime:
            self.last_checked = latest_mtime
        return has_higher_mtime

    def notify(self, path: Path) -> None:
        """Notify the watcher of a change to a path."""
        try:
            change_mtime = Path(path).stat().st_mtime_ns
        except FileNotFoundError:
            change_mtime = time_ns()
        self.last_notified = max(self.last_notified, change_mtime)

    @abc.abstractmethod
    def _get_latest_mtime(self) -> int:
        """Get the latest change mtime."""


class WatchfilesWatcher(WatcherBase):
    """A file and folder watcher using the watchfiles library."""

    def __init__(self) -> None:
        self.last_checked = 0
        self.last_notified = 0
        self._paths: list[Path] = []
        self._thread: _WatchfilesThread | None = None

    def update(self, files: Iterable[Path], folders: Iterable[Path]) -> None:
        """Update the folders/files to watch."""
        new_paths = [p for p in chain(files, folders) if p.exists()]
        if self._thread and new_paths == self._paths:
            self.check()
            return
        self._paths = new_paths
        if self._thread is not None:
            self._thread.stop()
        self._thread = _WatchfilesThread(self._paths, self.last_checked)
        self._thread.start()
        self.check()

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        if self._thread:
            self._thread.stop()

    def _get_latest_mtime(self) -> int:
        return self._thread.mtime if self._thread else 0


class Watcher(WatcherBase):
    """A simple file and folder watcher.

    For folders, only checks mtime of the folder and all subdirectories.
    So a file change won't be noticed, but only new/deleted files.
    """

    __slots__ = ("_files", "_folders", "last_checked")

    def __init__(self) -> None:
        self.last_checked = 0
        self.last_notified = 0
        self._files: list[Path] = []
        self._folders: list[Path] = []

    def update(self, files: Iterable[Path], folders: Iterable[Path]) -> None:
        """Update the folders/files to watch."""
        self._files = list(files)
        self._folders = list(folders)
        self.check()

    def _mtimes(self) -> Iterable[int]:
        for path in self._files:
            try:
                yield path.stat().st_mtime_ns
            except FileNotFoundError:
                yield time_ns()
        for path in self._folders:
            for dirpath, _, _ in walk(path):
                yield Path(dirpath).stat().st_mtime_ns

    def _get_latest_mtime(self) -> int:
        return max(self._mtimes())
