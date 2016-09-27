"""A simple file and folder watcher. """

import os
import time


class Watcher(object):
    """A simple file and folder watcher.

    For folders, only checks mtime of the folder and all subdirectories.
    So a file change won't be noticed, but only new/deleted files.
    """

    __slots__ = ['files', 'folders', 'last_checked']

    def __init__(self):
        self.files = []
        self.folders = []
        self.last_checked = time.time()

    def update(self, files, folders):
        """Update the folders/files to watch. """
        self.files = [path for path in files]
        self.folders = [path for path in folders]
        self.last_checked = time.time()

    def check(self):
        """Checks for changes. """
        for path in self.files:
            if os.stat(path).st_mtime > self.last_checked:
                self.last_checked = time.time()
                return True
        for path in self.folders:
            for dirpath, _, _ in os.walk(path):
                if os.stat(dirpath).st_mtime > self.last_checked:
                    self.last_checked = time.time()
                    return True
        self.last_checked = time.time()
        return False
