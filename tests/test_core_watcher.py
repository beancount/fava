from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from fava.core.watcher import Watcher
from fava.core.watcher import WatchfilesWatcher

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


ONE_MILLISECOND = 0.001
FIVE_MILLISECONDS = 0.005


@dataclass
class WatcherTestSet:
    """A set of paths to test the file watchers with."""

    tmp_path: Path
    file1: Path
    file2: Path
    folder: Path


@pytest.fixture
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
    time.sleep(FIVE_MILLISECONDS)
    watcher_paths.file1.write_text("test2")
    assert watcher.check()


def test_watcher_deleted_file(watcher_paths: WatcherTestSet) -> None:
    watcher = Watcher()
    watcher.update([watcher_paths.file1], [])
    assert not watcher.check()
    watcher_paths.file1.unlink()

    time.sleep(FIVE_MILLISECONDS)
    assert watcher.check()


def test_watcher_folder(watcher_paths: WatcherTestSet) -> None:
    (watcher_paths.folder / "bar").mkdir()

    watcher = Watcher()
    watcher.update([], [watcher_paths.folder])
    assert not watcher.check()

    time.sleep(FIVE_MILLISECONDS)
    (watcher_paths.folder / "bar2").mkdir()
    assert watcher.check()


def _watcher_poll_check(watcher: WatchfilesWatcher) -> bool:
    for _ in range(200):
        if watcher.check():
            return True
        time.sleep(ONE_MILLISECOND)

    return False


def test_watchfiles_watcher(watcher_paths: WatcherTestSet) -> None:
    watcher = WatchfilesWatcher()
    with watcher:
        assert not watcher.check()  # No thread set up yet.

    with watcher:
        watcher.update([watcher_paths.file1, watcher_paths.file2], [])
        assert not watcher.check()
        watcher_paths.file1.write_text("test2")
        assert _watcher_poll_check(watcher)

        watcher.update([watcher_paths.file1, watcher_paths.file2], [])
        assert not watcher.check()
        watcher_paths.file1.write_text("test2")
        assert _watcher_poll_check(watcher)

        watcher.update([watcher_paths.file1], [])
        assert not watcher.check()
        watcher_paths.file1.write_text("test2")
        assert _watcher_poll_check(watcher)

        # notify of change we already detected
        watcher.notify(watcher_paths.file1)
        assert not watcher.check()

        # delete
        watcher_paths.file1.unlink()
        assert _watcher_poll_check(watcher)

        # notify of deleted file
        watcher.notify(watcher_paths.file1)
        assert watcher.check()


def test_watchfiles_watcher_recognises_change_to_previously_deleted_file(
    watcher_paths: WatcherTestSet,
) -> None:
    watcher = WatchfilesWatcher()

    with watcher:
        watcher.update([watcher_paths.file1], [])

        watcher_paths.file1.unlink()
        assert _watcher_poll_check(watcher)

        # Recreate deleted file
        # sleep to ensure file stamp is greater than time_ns() taken on
        #  previous FileNotFoundError
        time.sleep(FIVE_MILLISECONDS)
        watcher_paths.file1.write_text("test-value-2")
        assert _watcher_poll_check(watcher)
        assert not watcher.check()
