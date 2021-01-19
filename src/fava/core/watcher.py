"""A simple file and folder watcher."""
import os
from typing import Iterable
from typing import List


class Watcher:
    """A simple file and folder watcher.

    For folders, only checks mtime of the folder and all subdirectories.
    So a file change won't be noticed, but only new/deleted files.
    """

    __slots__ = ["_files", "_folders", "_last_checked"]

    def __init__(self) -> None:
        self._files: List[str] = []
        self._folders: List[str] = []
        self._last_checked = 0

    def update(self, files: Iterable[str], folders: Iterable[str]) -> None:
        """Update the folders/files to watch.

        Args:
            files: A list of file paths.
            folders: A list of paths to folders.
        """
        self._files = list(files)
        self._folders = list(folders)
        self.check()

    def check(self) -> bool:
        """Check for changes.

        Returns:
            `True` if there was a file change in one of the files or folders,
            `False` otherwise.
        """
        latest_mtime = 0
        for path in self._files:
            try:
                mtime = os.stat(path).st_mtime_ns
            except FileNotFoundError:
                return True
            if mtime > latest_mtime:
                latest_mtime = mtime
        for path in self._folders:
            for dirpath, _, _ in os.walk(path):
                mtime = os.stat(dirpath).st_mtime_ns
                if mtime > latest_mtime:
                    latest_mtime = mtime

        changed = bool(latest_mtime != self._last_checked)
        self._last_checked = latest_mtime
        return changed
