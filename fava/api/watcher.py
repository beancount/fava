"""A simple file and folder watcher. """

import os


class Watcher(object):
    """A simple file and folder watcher.

    For folders, only checks mtime of the folder and all subdirectories.
    So a file change won't be noticed, but only new/deleted files.
    """

    __slots__ = ['files', 'folders', 'last_checked']

    def __init__(self):
        self.files = []
        self.folders = []
        self.last_checked = 0

    def update(self, files, folders):
        """Update the folders/files to watch. """
        self.files = [path for path in files]
        self.folders = [path for path in folders]
        self.check()

    def check(self):
        """Checks for changes. """
        latest_mtime = 0
        for path in self.files:
            mtime = os.stat(path).st_mtime_ns
            if mtime > latest_mtime:
                latest_mtime = mtime
        for path in self.folders:
            for dirpath, _, _ in os.walk(path):
                mtime = os.stat(dirpath).st_mtime_ns
                if mtime > latest_mtime:
                    latest_mtime = mtime

        changed = bool(latest_mtime != self.last_checked)
        self.last_checked = latest_mtime
        return changed
