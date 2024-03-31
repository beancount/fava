"""A simple file and folder watcher."""

from __future__ import annotations

import abc
import atexit
import logging
import threading
from os import walk
from pathlib import Path
from typing import Iterable
from typing import TYPE_CHECKING

from watchfiles import watch

if TYPE_CHECKING:  # pragma: no cover
    import types

    from watchfiles.main import Change


log = logging.getLogger(__name__)


class _WatchfilesThread(threading.Thread):
    def __init__(
        self, files: list[Path], folders: list[Path], mtime: int
    ) -> None:
        super().__init__(daemon=True)
        self._stop_event = threading.Event()
        self.mtime = mtime
        self._file_set = {f.absolute() for f in files}
        self._folder_set = {f.absolute() for f in folders}

    def stop(self) -> None:
        """Set the stop event for watchfiles and join the thread."""
        self._stop_event.set()
        self.join()

    def _is_relevant(self, _c: Change, path: str) -> bool:
        return Path(path) in self._file_set or any(
            Path(path).is_relative_to(d) for d in self._folder_set
        )

    def run(self) -> None:
        """Watch for changes."""
        atexit.register(self.stop)

        watch_paths = {f.parent for f in self._file_set} | self._folder_set

        for changes in watch(
            *watch_paths,
            stop_event=self._stop_event,
            ignore_permission_denied=True,
            watch_filter=self._is_relevant,
        ):
            for path in {change[1] for change in changes}:
                try:
                    change_mtime = Path(path).stat().st_mtime_ns
                except FileNotFoundError:
                    # set the change time to an artificial timestamp one
                    # nanosecond after the latest mtime.
                    change_mtime = self.mtime + 1
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
            change_mtime = max(self.last_notified, self.last_checked) + 1
        self.last_notified = max(self.last_notified, change_mtime)

    @abc.abstractmethod
    def _get_latest_mtime(self) -> int:
        """Get the latest change mtime."""


class WatchfilesWatcher(WatcherBase):
    """A file and folder watcher using the watchfiles library."""

    def __init__(self) -> None:
        self.last_checked = 0
        self.last_notified = 0
        self._paths: tuple[list[Path], list[Path]] = ([], [])
        self._thread: _WatchfilesThread | None = None

    def update(self, files: Iterable[Path], folders: Iterable[Path]) -> None:
        """Update the folders/files to watch."""
        existing_files = [p for p in files if p.exists()]
        existing_folders = [p for p in folders if p.is_dir()]
        new_paths = (existing_files, existing_folders)
        if self._thread and new_paths == self._paths:
            self.check()
            return
        self._paths = new_paths
        if self._thread is not None:
            self._thread.stop()
        self._thread = _WatchfilesThread(
            existing_files, existing_folders, self.last_checked
        )
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
                yield max(self.last_notified, self.last_checked) + 1
        for path in self._folders:
            for dirpath, _, _ in walk(path):
                yield Path(dirpath).stat().st_mtime_ns

    def _get_latest_mtime(self) -> int:
        return max(self._mtimes())
