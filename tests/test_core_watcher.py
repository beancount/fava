# pylint: disable=missing-docstring

import time

from fava.core.watcher import Watcher


def test_watcher_file(tmpdir):
    file1 = tmpdir.join("file1")
    file2 = tmpdir.join("file2")
    file1.write("test")
    file2.write("test")

    watcher = Watcher()
    watcher.update([str(file1), str(file2)], [])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    file1.write("test2")

    assert watcher.check()


def test_watcher_folder(tmpdir):
    folder = tmpdir.mkdir("folder")
    folder.mkdir("bar")

    watcher = Watcher()
    watcher.update([], [str(folder)])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    folder.mkdir("bar2")

    assert watcher.check()
