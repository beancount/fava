# pylint: disable=missing-docstring
import os
from pathlib import Path
from pprint import pformat
from typing import Any
from typing import Callable
from typing import Counter

import pytest
from beancount.loader import load_string

from fava.application import _load_file
from fava.application import app as fava_app
from fava.core import FavaLedger
from fava.core.budgets import parse_budgets


def data_file(filename: str) -> str:
    return str(Path(__file__).parent / "data" / filename)


EXAMPLE_FILE = data_file("long-example.beancount")
EXTENSION_REPORT_EXAMPLE_FILE = data_file("extension-report-example.beancount")

EXAMPLE_LEDGER = FavaLedger(EXAMPLE_FILE)

fava_app.testing = True
TEST_CLIENT = fava_app.test_client()

fava_app.config["BEANCOUNT_FILES"] = [
    EXAMPLE_FILE,
    EXTENSION_REPORT_EXAMPLE_FILE,
]
_load_file()


SNAPSHOT_UPDATE = bool(os.environ.get("SNAPSHOT_UPDATE"))
MSG = "Maybe snapshots need to be updated with `SNAPSHOT_UPDATE=1 make test`?"

# Keep track of multiple calls to snapshot in one test function to generate
# unique (simply numbered) file names for the snashop files.
SNAPS: Counter[Path] = Counter()


@pytest.fixture()
def snapshot(request) -> Callable[[Any], None]:
    file_path = Path(request.fspath)
    fn_name = request.function.__name__
    snap_dir = file_path.parent / "__snapshots__"
    if not snap_dir.exists():
        snap_dir.mkdir()

    def _snapshot_data(data) -> None:
        snap_file = snap_dir / f"{file_path.name}-{fn_name}"
        SNAPS[snap_file] += 1
        if SNAPS[snap_file] > 1:
            snap_file = (
                snap_dir / f"{file_path.name}-{fn_name}-{SNAPS[snap_file]}"
            )

        out = pformat(data)
        if not snap_file.exists():
            contents = ""
        else:
            with open(snap_file, encoding="utf-8") as snap_file_handle:
                contents = snap_file_handle.read()
        if SNAPSHOT_UPDATE:
            with open(snap_file, "w", encoding="utf-8") as snap_file_handle:
                snap_file_handle.write(out)
            return
        assert out == contents, MSG

    return _snapshot_data


@pytest.fixture
def app():
    return fava_app


@pytest.fixture
def test_client():
    return TEST_CLIENT


@pytest.fixture
def load_doc(request):
    return load_string(request.function.__doc__, dedent=True)


@pytest.fixture
def small_example_ledger():
    return FavaLedger(data_file("example.beancount"))


@pytest.fixture
def example_ledger():
    yield EXAMPLE_LEDGER
    EXAMPLE_LEDGER.filter(account=None, filter=None, time=None)


@pytest.fixture
def budgets_doc(request):
    entries, _, _ = load_string(request.function.__doc__, dedent=True)
    budgets, _ = parse_budgets(entries)
    return budgets
