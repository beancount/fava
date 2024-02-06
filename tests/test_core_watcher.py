from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from fava.core.watcher import Watcher

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


@dataclass
class WatcherTestSet:
    tmp_path: Path
    file1: Path
    file2: Path
    folder: Path


@pytest.fixture()
def watcher_paths(tmp_path: Path) -> WatcherTestSet:
    file1 = tmp_path / "file1"
    file2 = tmp_path / "file2"
    file1.write_text("test")
    file2.write_text("test")
    folder = tmp_path / "folder"
    folder.mkdir()
    return WatcherTestSet(
        tmp_path=tmp_path, file1=file1, file2=file2, folder=folder
    )


def test_watcher_file(watcher_paths: WatcherTestSet) -> None:
    watcher = Watcher()
    watcher.update([watcher_paths.file1, watcher_paths.file2], [])
    assert not watcher.check()
    time.sleep(0.005)
    watcher_paths.file1.write_text("test2")
    assert watcher.check()


def test_watcher_deleted_file(watcher_paths: WatcherTestSet) -> None:
    watcher = Watcher()
    watcher.update([watcher_paths.file1], [])
    assert not watcher.check()
    watcher_paths.file1.unlink()

    time.sleep(0.005)
    assert watcher.check()


def test_watcher_folder(watcher_paths: WatcherTestSet) -> None:
    (watcher_paths.folder / "bar").mkdir()

    watcher = Watcher()
    watcher.update([], [watcher_paths.folder])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(0.005)

    (watcher_paths.folder / "bar2").mkdir()

    assert watcher.check()
