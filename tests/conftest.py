# pylint: disable=missing-docstring

import os
from pathlib import Path
from pprint import pformat

import pytest

from beancount.loader import load_string
from fava.core import FavaLedger
from fava.application import _load_file, app as fava_app
from fava.core.budgets import parse_budgets


def create_app(bfile):
    key = "BEANCOUNT_FILES"
    if (key not in fava_app.config) or (fava_app.config[key] != [bfile]):
        fava_app.config[key] = [bfile]
        _load_file()


def data_file(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


EXAMPLE_FILE = data_file("long-example.beancount")
EXTENSION_REPORT_EXAMPLE_FILE = data_file("extension-report-example.beancount")

API = FavaLedger(EXAMPLE_FILE)

fava_app.testing = True
TEST_CLIENT = fava_app.test_client()
create_app(EXAMPLE_FILE)


SNAPSHOT_UPDATE = bool(os.environ.get("SNAPSHOT_UPDATE"))
MSG = "Maybe snapshots need to be updated with `SNAPSHOT_UPDATE=1 make test`?"


@pytest.fixture
def snapshot(request):
    file_path = Path(request.fspath)
    fn_name = request.function.__name__
    snap_dir = file_path.parent / "__snapshots__"
    if not snap_dir.exists():
        snap_dir.mkdir()

    def _snapshot_data(data, item=None):
        snap_file = (
            snap_dir / f"{file_path.name}-{fn_name}-{item}"
            if item
            else snap_dir / f"{file_path.name}-{fn_name}"
        )
        out = pformat(data)
        if not snap_file.exists():
            contents = ""
        else:
            contents = open(snap_file).read()
        if SNAPSHOT_UPDATE:
            open(snap_file, "w").write(out)
            return
        assert out == contents, MSG

    return _snapshot_data


@pytest.fixture
def extension_report_app():
    create_app(EXTENSION_REPORT_EXAMPLE_FILE)
    return fava_app


@pytest.fixture
def app():
    create_app(EXAMPLE_FILE)
    return fava_app


@pytest.fixture
def test_client():
    return TEST_CLIENT


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def extension_report_ledger():
    return FavaLedger(EXTENSION_REPORT_EXAMPLE_FILE)


@pytest.fixture
def small_example_ledger():
    return FavaLedger(data_file("example.beancount"))


@pytest.fixture
def example_ledger():
    yield API
    API.filter(account=None, filter=None, time=None)


@pytest.fixture
def budgets_doc(request):
    entries, _, _ = load_string(request.function.__doc__, dedent=True)
    budgets, _ = parse_budgets(entries)
    return budgets
