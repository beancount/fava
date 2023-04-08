"""Test fixtures."""
# pylint: disable=redefined-outer-name
from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from pprint import pformat
from textwrap import dedent
from typing import Any
from typing import Callable
from typing import Counter
from typing import TYPE_CHECKING

import pytest

from fava.application import _load_file
from fava.application import app as fava_app
from fava.beans.abc import Custom
from fava.beans.abc import Directive
from fava.beans.load import load_string
from fava.core import FavaLedger
from fava.core.budgets import BudgetDict
from fava.core.budgets import parse_budgets

if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal
    from typing import TypeAlias
    from typing import TypeGuard

    from flask.app import Flask
    from flask.testing import FlaskClient

    from fava.beans.types import LoaderResult

TEST_DATA_DIR = Path(__file__).parent / "data"


fava_app.testing = True
fava_app.config["BEANCOUNT_FILES"] = [
    str(TEST_DATA_DIR / filename)
    for filename in [
        "long-example.beancount",
        "example.beancount",
        "extension-report-example.beancount",
        "import.beancount",
        "query-example.beancount",
        "errors.beancount",
        "off-by-one.beancount",
    ]
]
_load_file()


SNAPSHOT_UPDATE = bool(os.environ.get("SNAPSHOT_UPDATE"))
MSG = "Maybe snapshots need to be updated with `SNAPSHOT_UPDATE=1 make test`?"

# Keep track of multiple calls to snapshot in one test function to generate
# unique (simply numbered) file names for the snashop files.
SNAPS: Counter[Path] = Counter()


SnapshotFunc = Callable[[Any], None]


@pytest.fixture()
def snapshot(request: pytest.FixtureRequest) -> SnapshotFunc:
    """Create a snaphot for some given data."""
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
        out = re.sub(r"\d+ days ago", "X days ago", out)
        for dir_path, replacement in [
            (str(TEST_DATA_DIR), "TEST_DATA_DIR"),
        ]:
            if os.name == "nt":
                search = dir_path.replace("\\", "\\\\") + "\\\\"
                out = out.replace(search, replacement + "/")
            else:
                out = out.replace(dir_path, replacement)
        contents = (
            "" if not snap_file.exists() else snap_file.read_text("utf-8")
        )
        if SNAPSHOT_UPDATE:
            snap_file.write_text(out, "utf-8")
            return

        assert out == contents, MSG

    return _snapshot_data


@pytest.fixture()
def test_data_dir() -> Path:
    """Get the path to the test data files."""
    return TEST_DATA_DIR


@pytest.fixture()
def app() -> Flask:
    """Get the Fava Flask app."""
    return fava_app


@pytest.fixture()
def test_client() -> FlaskClient:
    """Get the test client for the Fava Flask app."""
    return fava_app.test_client()


@pytest.fixture()
def load_doc(request: pytest.FixtureRequest) -> LoaderResult:
    """Load the docstring as a Beancount file."""
    contents = dedent(request.function.__doc__)
    return load_string(contents)


@pytest.fixture()
def load_doc_entries(load_doc: LoaderResult) -> list[Directive]:
    """Load the docstring as Beancount entries."""
    entries, _errors, _options = load_doc
    return entries


def _is_custom_entries_list(
    entries: list[Directive],
) -> TypeGuard[list[Custom]]:
    return all(isinstance(e, Custom) for e in entries)


@pytest.fixture()
def load_doc_custom_entries(load_doc_entries: list[Directive]) -> list[Custom]:
    """Load the docstring as Beancount custom entries."""
    assert _is_custom_entries_list(load_doc_entries)
    return load_doc_entries


@pytest.fixture()
def budgets_doc(load_doc_custom_entries: list[Custom]) -> BudgetDict:
    """Load the budgets from the custom entries in the docstring."""
    budgets, _ = parse_budgets(load_doc_custom_entries)
    return budgets


if TYPE_CHECKING:
    #: Slugs of the ledgers that are loaded for the test cases.
    LedgerSlug: TypeAlias = Literal[
        "example",
        "query-example",
        "long-example",
        "extension-report",
        "import",
        "off-by-one",
    ]
    GetFavaLedger: TypeAlias = Callable[[LedgerSlug], FavaLedger]


@pytest.fixture()
def get_ledger() -> GetFavaLedger:
    """Getter for one of the loaded ledgers."""

    def _get_ledger(name: LedgerSlug) -> FavaLedger:
        loaded_ledgers = fava_app.config["LEDGERS"]
        assert name in loaded_ledgers, loaded_ledgers.keys()
        ledger = fava_app.config["LEDGERS"][name]
        assert isinstance(ledger, FavaLedger)
        return ledger

    return _get_ledger


@pytest.fixture()
def small_example_ledger(get_ledger: GetFavaLedger) -> FavaLedger:
    """Get the small example ledger."""
    return get_ledger("example")


@pytest.fixture()
def example_ledger(get_ledger: GetFavaLedger) -> FavaLedger:
    """Get the long example ledger."""
    return get_ledger("long-example")
