"""A simple file and folder watcher."""

import os


class Watcher(object):
    """A simple file and folder watcher.

    For folders, only checks mtime of the folder and all subdirectories.
    So a file change won't be noticed, but only new/deleted files.
    """

    __slots__ = ['_files', '_folders', '_last_checked']

    def __init__(self):
        self._files = []
        self._folders = []
        self._last_checked = 0

    def update(self, files, folders):
        """Update the folders/files to watch.

        Args:
            files: A list of file paths.
            folders: A list of paths to folders.

        """
        self._files = [path for path in files]
        self._folders = [path for path in folders]
        self.check()

    def check(self):
        """Check for changes.

        Returns:
            `True` if there was a file change in one of the files or folders,
            `False` otherwise.

        """
        latest_mtime = 0
        for path in self._files:
            mtime = os.stat(path).st_mtime_ns
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
