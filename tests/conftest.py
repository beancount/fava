"""Test fixtures."""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from pprint import pformat
from textwrap import dedent
from typing import Any
from typing import TYPE_CHECKING

import pytest

from fava.application import create_app
from fava.beans.abc import Custom
from fava.beans.load import load_string
from fava.core import FavaLedger
from fava.core.budgets import parse_budgets
from fava.core.charts import dumps
from fava.util.date import local_today

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Generator
    from typing import Literal
    from typing import Protocol
    from typing import TypeAlias
    from typing import TypeGuard

    from flask.app import Flask
    from flask.testing import FlaskClient

    from fava.beans.abc import Directive
    from fava.beans.types import LoaderResult
    from fava.core.budgets import BudgetDict

    class SnapshotFunc(Protocol):
        """Callable protocol for the snapshot function."""

        def __call__(
            self,
            data: Any,
            /,
            *,
            name: str = ...,
            json: bool = ...,
        ) -> None:
            """Check snapshot."""


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to the test data files."""
    return Path(__file__).parent / "data"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add pytest options to influence snapshot behaviour."""
    parser.addoption(
        "--snapshot-clean",
        action="store_true",
        dest="SNAPSHOT_CLEAN",
        help="Clean unused snapshot files",
    )
    parser.addoption(
        "--snapshot-ignore",
        action="store_true",
        dest="SNAPSHOT_IGNORE",
        help="Ignore snapshot files",
    )
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        dest="SNAPSHOT_UPDATE",
        help="Update snapshot files",
    )


@pytest.fixture(scope="session")
def compare_snapshot(
    request: pytest.FixtureRequest,
) -> Generator[Callable[[str, str], None], None, None]:
    """Compare on-disk snapshots, possibly updating if configured."""
    snap_dir = Path(__file__).parent / "__snapshots__"
    if not snap_dir.exists():
        snap_dir.mkdir()

    should_update = request.config.getoption("SNAPSHOT_UPDATE")
    seen_snapshots = set()

    def check_snapshot(name: str, expected: str) -> None:
        snap_file = snap_dir / name
        seen_snapshots.add(snap_file)

        contents = snap_file.read_text("utf-8") if snap_file.exists() else ""
        if should_update:
            if expected != contents:
                snap_file.write_text(expected, "utf-8")
        else:
            assert expected == contents, (
                "Snaphot test failed. Snapshots can be updated with "
                "`pytest --snapshot-update`"
            )

    yield check_snapshot

    # Cleanup unused snapshot files if requested
    if request.config.getoption("SNAPSHOT_CLEAN"):
        existing_snapshots = set(snap_dir.iterdir())
        extra_snapshots = existing_snapshots - seen_snapshots
        for extra_snapshot in extra_snapshots:
            extra_snapshot.unlink()


class SnapCount:
    """Count the number of snapshots within a function."""

    def __init__(self) -> None:
        self.count = 0

    def filename(self, base: str, name: str | None) -> str:
        """Get the filename, possibly including the count."""
        self.count += 1
        if name:
            return f"{base}-{name}"
        if self.count > 1:
            return f"{base}-{self.count}"
        return base


@pytest.fixture
def snapshot(
    request: pytest.FixtureRequest,
    test_data_dir: Path,
    compare_snapshot: Callable[[str, str], None],
) -> SnapshotFunc:
    """Create a snaphot for some given data."""
    fn_name = request.function.__name__
    module_name = request.path.stem
    snap_count = SnapCount()

    def snapshot_data(
        data: Any,
        *,
        name: str | None = None,
        json: bool = False,
    ) -> None:
        if request.config.getoption("SNAPSHOT_IGNORE"):
            # For the tests runs with old dependencies, we avoid comparing
            # the snapshots, as they might change in subtle ways between
            # dependency versions.
            return

        filename = snap_count.filename(f"{module_name}-{fn_name}", name)

        if json:
            data = dumps(data)
            filename += ".json"

        # print strings directly, otherwise try pretty-printing
        out = data if isinstance(data, str) else pformat(data)
        # replace today
        today = local_today()
        out = out.replace(str(today), "TODAY")
        # replace entry hashes
        out = re.sub(r'_hash": "[0-9a-f]+', '_hash": "ENTRY_HASH', out)
        out = re.sub(r"context-[0-9a-f]+", "context-ENTRY_HASH", out)
        out = re.sub(
            r"data-entry=\\\"[0-9a-f]+", 'data-entry=\\"ENTRY_HASH', out
        )
        # replace mtimes
        out = re.sub(r"mtime=\d+", "mtime=MTIME", out)
        out = re.sub(r'id="ledger-mtime">\d+', 'id="ledger-mtime">MTIME', out)
        # replace env-dependant info
        out = out.replace('have_excel": false', 'have_excel": true')

        for dir_path, replacement in [
            (f"{test_data_dir}{os.sep}", "TEST_DATA_DIR/"),
        ]:
            if sys.platform == "win32":
                out = out.replace(
                    dir_path.replace(os.sep, os.sep * 2), replacement
                )
                out = out.replace(
                    dir_path.replace(os.sep, os.sep * 4), replacement
                )
            else:
                out = out.replace(dir_path, replacement)

        compare_snapshot(filename, out)

    return snapshot_data


@pytest.fixture(scope="session")
def app(test_data_dir: Path) -> Flask:
    """Get the Fava Flask app."""
    fava_app = create_app(
        [
            test_data_dir / filename
            for filename in [
                "long-example.beancount",
                "example.beancount",
                "extension-report-example.beancount",
                "import.beancount",
                "query-example.beancount",
                "errors.beancount",
                "off-by-one.beancount",
                "invalid-unicode.beancount",
            ]
        ],
        load=True,
    )
    fava_app.testing = True
    return fava_app


@pytest.fixture
def app_in_tmp_dir(test_data_dir: Path, tmp_path: Path) -> Flask:
    """Get a Fava Flask app in a tmp_dir."""
    ledger_path = tmp_path / "edit-example.beancount"
    shutil.copy(test_data_dir / "edit-example.beancount", ledger_path)
    ledger_path.chmod(tmp_path.stat().st_mode)
    fava_app = create_app([str(ledger_path)], load=True)
    fava_app.testing = True
    return fava_app


@pytest.fixture
def test_client(app: Flask) -> FlaskClient:
    """Get the test client for the Fava Flask app."""
    return app.test_client()


@pytest.fixture
def load_doc(request: pytest.FixtureRequest) -> LoaderResult:
    """Load the docstring as a Beancount file."""
    contents = dedent(request.function.__doc__)
    return load_string(contents)


@pytest.fixture
def load_doc_entries(load_doc: LoaderResult) -> list[Directive]:
    """Load the docstring as Beancount entries."""
    entries, _errors, _options = load_doc
    return entries


def _is_custom_entries_list(
    entries: list[Directive],
) -> TypeGuard[list[Custom]]:
    return all(isinstance(e, Custom) for e in entries)


@pytest.fixture
def load_doc_custom_entries(load_doc_entries: list[Directive]) -> list[Custom]:
    """Load the docstring as Beancount custom entries."""
    assert _is_custom_entries_list(load_doc_entries)
    return load_doc_entries


@pytest.fixture
def budgets_doc(load_doc_custom_entries: list[Custom]) -> BudgetDict:
    """Load the budgets from the custom entries in the docstring."""
    budgets, _ = parse_budgets(load_doc_custom_entries)
    return budgets


if TYPE_CHECKING:  # pragma: no cover
    #: Slugs of the ledgers that are loaded for the test cases.
    LedgerSlug: TypeAlias = Literal[
        "example",
        "query-example",
        "long-example",
        "extension-report",
        "import",
        "off-by-one",
        "invalid-unicode",
    ]
    GetFavaLedger: TypeAlias = Callable[[LedgerSlug], FavaLedger]


@pytest.fixture(scope="session")
def get_ledger(app: Flask) -> GetFavaLedger:
    """Getter for one of the loaded ledgers."""

    def _get_ledger(name: LedgerSlug) -> FavaLedger:
        ledger = app.config["LEDGERS"][name]
        assert isinstance(ledger, FavaLedger)
        return ledger

    return _get_ledger


@pytest.fixture
def small_example_ledger(get_ledger: GetFavaLedger) -> FavaLedger:
    """Get the small example ledger."""
    return get_ledger("example")


@pytest.fixture
def example_ledger(get_ledger: GetFavaLedger) -> FavaLedger:
    """Get the long example ledger."""
    return get_ledger("long-example")
