# pylint: disable=missing-docstring
from __future__ import annotations

import time
from pathlib import Path

from fava.core.watcher import Watcher


def test_watcher_file(tmp_path: Path) -> None:
    file1 = tmp_path / "file1"
    file2 = tmp_path / "file2"
    file1.write_text("test")
    file2.write_text("test")

    watcher = Watcher()
    watcher.update([str(file1), str(file2)], [])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    file1.write_text("test2")

    assert watcher.check()


def test_watcher_deleted_file(tmp_path: Path) -> None:
    file1 = tmp_path / "file1"
    file1.write_text("test")

    watcher = Watcher()
    watcher.update([str(file1)], [])
    assert not watcher.check()

    file1.unlink()
    assert watcher.check()


def test_watcher_folder(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "bar").mkdir()

    watcher = Watcher()
    watcher.update([], [str(folder)])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    (folder / "bar2").mkdir()

    assert watcher.check()
