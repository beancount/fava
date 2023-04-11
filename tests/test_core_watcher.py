from __future__ import annotations

import time
from typing import TYPE_CHECKING

from fava.core.watcher import Watcher

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_watcher_file(tmp_path: Path) -> None:
    file1 = tmp_path / "file1"
    file2 = tmp_path / "file2"
    file1.write_text("test")
    file2.write_text("test")

    watcher = Watcher()
    watcher.update([file1, file2], [])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(0.05)

    file1.write_text("test2")

    assert watcher.check()


def test_watcher_deleted_file(tmp_path: Path) -> None:
    file1 = tmp_path / "file1"
    file1.write_text("test")

    watcher = Watcher()
    watcher.update([file1], [])
    assert not watcher.check()

    file1.unlink()
    assert watcher.check()


def test_watcher_folder(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "bar").mkdir()

    watcher = Watcher()
    watcher.update([], [folder])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(0.05)

    (folder / "bar2").mkdir()

    assert watcher.check()
