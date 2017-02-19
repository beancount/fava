import time

from fava.core.watcher import Watcher


def test_watcher_file(tmpdir):
    foo = tmpdir.join('foo')
    bar = tmpdir.join('bar')
    foo.write('test')
    bar.write('test')

    watcher = Watcher()
    watcher.update([str(foo), str(bar)], [])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    foo.write('test2')

    assert watcher.check()


def test_watcher_folder(tmpdir):
    foo = tmpdir.mkdir('foo')
    foo.mkdir('bar')

    watcher = Watcher()
    watcher.update([], [str(foo)])
    assert not watcher.check()

    # time.time is too precise
    time.sleep(1)

    foo.mkdir('bar2')

    assert watcher.check()
