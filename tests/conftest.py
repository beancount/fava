# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name
from __future__ import annotations

import datetime
import os
from pathlib import Path
from pprint import pformat
from textwrap import dedent
from typing import Any
from typing import Callable
from typing import Counter
from typing import TYPE_CHECKING

import pytest
from flask.app import Flask
from flask.testing import FlaskClient
from pytest import FixtureRequest

from fava.application import _load_file
from fava.application import app as fava_app
from fava.beans.abc import Custom
from fava.beans.abc import Directive
from fava.beans.load import load_string
from fava.core import FavaLedger
from fava.core.budgets import BudgetDict
from fava.core.budgets import parse_budgets

if TYPE_CHECKING:
    from typing import TypeGuard

    from fava.beans.types import LoaderResult

TESTS_DIR = Path(__file__).parent


def data_file(filename: str) -> str:
    return str(TESTS_DIR / "data" / filename)


LONG_EXAMPLE_FILE = data_file("long-example.beancount")
EXAMPLE_FILE = data_file("example.beancount")

EXAMPLE_LEDGER = FavaLedger(LONG_EXAMPLE_FILE)

fava_app.testing = True
TEST_CLIENT = fava_app.test_client()

fava_app.config["BEANCOUNT_FILES"] = [
    LONG_EXAMPLE_FILE,
    EXAMPLE_FILE,
    data_file("extension-report-example.beancount"),
    data_file("import.beancount"),
    data_file("query-example.beancount"),
    data_file("errors.beancount"),
]
_load_file()


SNAPSHOT_UPDATE = bool(os.environ.get("SNAPSHOT_UPDATE"))
MSG = "Maybe snapshots need to be updated with `SNAPSHOT_UPDATE=1 make test`?"

# Keep track of multiple calls to snapshot in one test function to generate
# unique (simply numbered) file names for the snashop files.
SNAPS: Counter[Path] = Counter()


SnapshotFunc = Callable[[Any], None]


@pytest.fixture()
def snapshot(request: FixtureRequest) -> SnapshotFunc:
    fspath = getattr(request, "fspath")  # noqa: B009
    file_path = Path(getattr(request, "path", fspath))
    fn_name = request.function.__name__
    snap_dir = file_path.parent / "__snapshots__"
    if not snap_dir.exists():
        snap_dir.mkdir()

    def _snapshot_data(data: Any) -> None:
        snap_file = snap_dir / f"{file_path.name}-{fn_name}"
        SNAPS[snap_file] += 1
        if SNAPS[snap_file] > 1:
            snap_file = (
                snap_dir / f"{file_path.name}-{fn_name}-{SNAPS[snap_file]}"
            )

        # print strings directly, otherwise try pretty-printing
        out = data if isinstance(data, str) else pformat(data)
        out = out.replace(str(datetime.date.today()), "TODAY")
        for dir_path, replacement in [
            (str(TESTS_DIR / "data"), "TEST_DATA_DIR"),
        ]:
            if os.name == "nt":
                search = dir_path.replace("\\", "\\\\") + "\\\\"
                out = out.replace(search, replacement + "/")
            else:
                out = out.replace(dir_path, replacement)
        if not snap_file.exists():
            contents = ""
        else:
            contents = snap_file.read_text("utf-8")
        if SNAPSHOT_UPDATE:
            snap_file.write_text(out, "utf-8")
            return

        assert out == contents, MSG

    return _snapshot_data


@pytest.fixture
def app() -> Flask:
    return fava_app


@pytest.fixture
def test_client() -> FlaskClient:
    return TEST_CLIENT


@pytest.fixture
def load_doc(request: FixtureRequest) -> LoaderResult:
    contents = dedent(request.function.__doc__)
    return load_string(contents)


def is_custom_entries_list(
    entries: list[Directive],
) -> TypeGuard[list[Custom]]:
    return all(isinstance(e, Custom) for e in entries)


@pytest.fixture
def load_doc_custom_entries(load_doc: LoaderResult) -> list[Custom]:
    entries, _errors, _options = load_doc
    assert is_custom_entries_list(entries)
    return entries


@pytest.fixture
def small_example_ledger() -> FavaLedger:
    return FavaLedger(data_file("example.beancount"))


@pytest.fixture
def example_ledger() -> FavaLedger:
    return EXAMPLE_LEDGER


@pytest.fixture
def budgets_doc(load_doc: LoaderResult) -> BudgetDict:
    entries, _, _ = load_doc
    assert is_custom_entries_list(entries)
    budgets, _ = parse_budgets(entries)
    return budgets
