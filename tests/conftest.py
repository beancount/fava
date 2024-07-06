"""Test fixtures."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from pprint import pformat
from textwrap import dedent
from typing import Any
from typing import Callable
from typing import Counter
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


@pytest.fixture(scope="module")
def module_path(request: pytest.FixtureRequest) -> Path:
    """Path to the tested module."""
    fspath = getattr(request, "fspath")  # noqa: B009
    return Path(getattr(request, "path", fspath))


@pytest.fixture(scope="module")
def snap_count() -> Counter[str]:
    """Counter for the number of snapshots per function in a module."""
    return Counter()


@pytest.fixture(scope="module")
def snap_dir(module_path: Path) -> Path:
    """Path to snapshot directory."""
    snap_dir = module_path.parent / "__snapshots__"
    if not snap_dir.exists():
        snap_dir.mkdir()
    return snap_dir


@pytest.fixture
def snapshot(
    request: pytest.FixtureRequest,
    test_data_dir: Path,
    module_path: Path,
    snap_dir: Path,
    snap_count: Counter[str],
) -> SnapshotFunc:
    """Create a snaphot for some given data."""
    fn_name = request.function.__name__
    module_name = module_path.stem

    def snapshot_data(
        data: Any,
        name: str | None = None,
        *,
        json: bool = False,
    ) -> None:
        if os.environ.get("SNAPSHOT_IGNORE"):
            # For the tests runs with old dependencies, we avoid comparing
            # the snapshots, as they might change in subtle ways between
            # dependency versions.
            return

        snap_count[fn_name] += 1
        filename = f"{module_name}-{fn_name}"
        if name:
            filename = f"{filename}-{name}"
        elif snap_count[fn_name] > 1:
            filename = f"{filename}-{snap_count[fn_name]}"

        if json:
            if not isinstance(data, str):
                data = dumps(data)
            filename += ".json"

        snap_file = snap_dir / filename

        # print strings directly, otherwise try pretty-printing
        out = data if isinstance(data, str) else pformat(data)
        # replace today
        today = local_today()
        out = out.replace(str(today), "TODAY")
        # replace entry hashes
        out = re.sub(r'"[0-9a-f]{32}', '"ENTRY_HASH', out)
        out = re.sub(r"context-[0-9a-f]{32}", "context-ENTRY_HASH", out)
        # replace mtimes
        out = re.sub(r"mtime=\d+", "mtime=MTIME", out)
        out = re.sub(r'id="ledger-mtime">\d+', 'id="ledger-mtime">MTIME', out)
        # replace env-dependant info
        out = out.replace('have_excel": false', 'have_excel": true')

        for dir_path, replacement in [
            (str(test_data_dir), "TEST_DATA_DIR"),
        ]:
            if os.name == "nt":
                search = dir_path.replace("\\", "\\\\") + "\\\\"
                out = out.replace(search, replacement + "/")
            else:
                out = out.replace(dir_path, replacement)

        if os.environ.get("SNAPSHOT_UPDATE"):
            snap_file.write_text(out, "utf-8")
        else:
            contents = (
                snap_file.read_text("utf-8") if snap_file.exists() else ""
            )
            assert out == contents, (
                "Snaphot test failed. Snapshots can be updated with "
                "`SNAPSHOT_UPDATE=1 pytest`"
            )

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
        loaded_ledgers = app.config["LEDGERS"]
        assert name in loaded_ledgers, loaded_ledgers.keys()
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
