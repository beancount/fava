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

from watchfiles import DefaultFilter
from watchfiles import watch

if TYPE_CHECKING:  # pragma: no cover
    import types
    from typing import Callable

    from watchfiles.main import Change


log = logging.getLogger(__name__)


class _WatchfilesThread(threading.Thread):
    """Class for the watchfiles watcher threads.

    We use two separated threads since we want to recursively watch directories
    and for paths, we need to watch the parent directory (to check changes done
    by file replacements by some editors) non-recursively (for performance).
    """

    def __init__(
        self,
        paths: set[Path],
        mtime: int,
        *,
        is_relevant: Callable[[Change, str], bool] | None = None,
        recursive: bool = False,
    ) -> None:
        super().__init__(daemon=True)
        self.paths = paths
        self.mtime = mtime
        self._is_relevant = is_relevant or DefaultFilter()
        self._recursive = recursive
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Set the stop event for watchfiles and join the thread."""
        self._stop_event.set()
        self.join()

    def run(self) -> None:
        """Watch for changes."""
        atexit.register(self.stop)

        for changes in watch(
            *self.paths,
            recursive=self._recursive,
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


class _FilesWatchfilesThread(_WatchfilesThread):
    def __init__(self, files: set[Path], mtime: int) -> None:
        paths = {f.parent for f in files}

        def is_relevant(_c: Change, path: str) -> bool:
            return Path(path) in files

        super().__init__(
            paths, mtime, is_relevant=is_relevant, recursive=False
        )


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
        self._paths: tuple[set[Path], set[Path]] | None = None
        self._watchers: tuple[_WatchfilesThread, _WatchfilesThread] | None = (
            None
        )

    def update(self, files: Iterable[Path], folders: Iterable[Path]) -> None:
        """Update the folders/files to watch."""
        files_set = {p.absolute() for p in files if p.exists()}
        folders_set = {p.absolute() for p in folders if p.is_dir()}
        new_paths = (files_set, folders_set)
        if self._watchers and new_paths == self._paths:
            self.check()
            return
        self._paths = new_paths
        if self._watchers:
            self._watchers[0].stop()
            self._watchers[1].stop()
        self._watchers = (
            _FilesWatchfilesThread(files_set, self.last_checked),
            _WatchfilesThread(folders_set, self.last_checked, recursive=True),
        )
        self._watchers[0].start()
        self._watchers[1].start()
        self.check()

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        if self._watchers:
            self._watchers[0].stop()
            self._watchers[1].stop()

    def _get_latest_mtime(self) -> int:
        return (
            max(self._watchers[0].mtime, self._watchers[1].mtime)
            if self._watchers
            else 0
        )


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
