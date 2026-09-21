from __future__ import annotations

import datetime
import runpy
from dataclasses import replace
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest
from beangulp.importer import Importer

from fava.beans.abc import Note
from fava.beans.abc import Transaction
from fava.core.ingest import FileImportInfo
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.core.ingest import ImportConfigConfigNotASequenceError
from fava.core.ingest import ImportConfigDuplicateImporterError
from fava.core.ingest import ImportConfigHooksNotASequenceCallablesError
from fava.core.ingest import ImportConfigInvalidImporterError
from fava.core.ingest import ImportConfigMissingConfigError
from fava.core.ingest import ImportConfigRunpyError
from fava.core.ingest import ImporterExtractError
from fava.core.ingest import ImporterInvalidTypeError
from fava.core.ingest import load_import_config
from fava.core.ingest import WrappedImporter
from fava.helpers import FavaAPIError
from fava.serialisation import serialise
from fava.util.date import local_today

try:
    from typing import override
except ImportError:  # pragma: no cover
    from typing_extensions import override

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Sequence

    from fava.beans.abc import Directive
    from fava.core import FavaLedger
    from fava.core.ingest import HookOutput

    from .conftest import GetFavaLedger
    from .conftest import SnapshotFunc


def test_ingest_file_import_info(
    test_data_dir: Path, get_ledger: GetFavaLedger
) -> None:
    ingest_ledger = get_ledger("import")
    assert ingest_ledger.ingest.loaded_config
    ingest_ledger.ingest.load_file()
    assert ingest_ledger.ingest.loaded_config
    importer = next(
        iter(ingest_ledger.ingest.loaded_config.importers.values())
    )
    assert importer

    csv_path = test_data_dir / "import.csv"
    info = importer.file_import_info(csv_path)
    assert info.account == "Assets:Checking"


class MinimalImporter(Importer):
    def __init__(self, acc: str = "Assets:Checking") -> None:
        self.acc = acc

    @override
    @property
    def name(self) -> str:
        return f"MinimalImporter({self.acc})"

    @override
    def identify(self, filepath: str) -> bool:
        return self.acc in filepath

    @override
    def account(self, filepath: str) -> str:
        return self.acc


def test_ingest_file_import_info_minimal_importer(test_data_dir: Path) -> None:
    csv_path = test_data_dir / "import.csv"

    importer = WrappedImporter(MinimalImporter())
    info = importer.file_import_info(csv_path)
    assert info == FileImportInfo(
        "MinimalImporter(Assets:Checking)",
        "Assets:Checking",
        local_today(),
        "import.csv",
    )


class AccountNameErrors(MinimalImporter):
    @override
    def account(self, filepath: str) -> str:
        msg = "Some error reason..."
        raise ValueError(msg)


def test_ingest_file_import_info_account_method_errors(
    test_data_dir: Path,
) -> None:
    csv_path = test_data_dir / "import.csv"

    importer = WrappedImporter(AccountNameErrors())
    with pytest.raises(FavaAPIError) as err:
        importer.file_import_info(csv_path)
    assert "Some error reason..." in err.value.message


class IdentifyErrors(MinimalImporter):
    @override
    def identify(self, filepath: str) -> bool:
        msg = "IDENTIFY_ERRORS"
        raise ValueError(msg)


def test_ingest_identify_errors(test_data_dir: Path) -> None:
    csv_path = test_data_dir / "import.csv"

    importer = WrappedImporter(IdentifyErrors())
    with pytest.raises(FavaAPIError) as err:
        importer.identify(csv_path)
    assert "IDENTIFY_ERRORS" in err.value.message


class ImporterNameErrors(MinimalImporter):
    @override
    @property
    def name(self) -> str:
        msg = "GET_NAME_WILL_ERROR"
        raise ValueError(msg)


def test_ingest_get_name_errors() -> None:
    importer = WrappedImporter(ImporterNameErrors())
    with pytest.raises(FavaAPIError) as err:
        assert importer.name
    assert "GET_NAME_WILL_ERROR" in err.value.message


class ImporterNameInvalidType(MinimalImporter):
    @override
    @property
    def name(self) -> str:
        return False  # type: ignore[return-value]  # ty:ignore[invalid-return-type]


def test_ingest_get_name_invalid_type() -> None:
    importer = WrappedImporter(ImporterNameInvalidType())
    with pytest.raises(ImporterInvalidTypeError):
        assert importer.name


@pytest.mark.parametrize(
    ("mod", "error"),
    [
        ({}, ImportConfigMissingConfigError),
        ({"CONFIG": object()}, ImportConfigConfigNotASequenceError),
        ({"CONFIG": [object()]}, ImportConfigInvalidImporterError),
        (
            {"CONFIG": [MinimalImporter(), MinimalImporter()]},
            ImportConfigDuplicateImporterError,
        ),
        (
            {"CONFIG": [], "HOOKS": object()},
            ImportConfigHooksNotASequenceCallablesError,
        ),
        (
            {"CONFIG": [], "HOOKS": [object()]},
            ImportConfigHooksNotASequenceCallablesError,
        ),
    ],
)
def test_load_import_config_errors(
    mod: dict[str, Any],
    error: type[Exception],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runpy, "run_path", lambda _: mod)
    with pytest.raises(error):
        load_import_config(Path())


@pytest.mark.parametrize(
    ("mod"),
    [
        {"CONFIG": []},
        {"CONFIG": [], "HOOKS": []},
        {"CONFIG": (), "HOOKS": ()},
        {"CONFIG": [MinimalImporter()], "HOOKS": []},
        {"CONFIG": (MinimalImporter(),), "HOOKS": (lambda x: x,)},
    ],
)
def test_load_import_config_ok(
    mod: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runpy, "run_path", lambda _: mod)
    assert load_import_config(Path())


def test_load_import_config(test_data_dir: Path) -> None:
    with pytest.raises(ImportConfigRunpyError):
        load_import_config(test_data_dir / "errors.beancount")
    with pytest.raises(ImportConfigMissingConfigError):
        load_import_config(Path(__file__))


def test_ingest_errors_file_does_not_exist(
    get_ledger: GetFavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ingest_ledger = get_ledger("import")
    with monkeypatch.context() as m:
        m.setattr(
            ingest_ledger.fava_options, "import_config", "does_not_exist.py"
        )
        ingest_ledger.ingest.load_file()
        assert ingest_ledger.ingest.errors

    with monkeypatch.context() as m:
        m.setattr(
            ingest_ledger.fava_options, "import_config", "errors.beancount"
        )
        ingest_ledger.ingest.load_file()
        assert ingest_ledger.ingest.errors

    ingest_ledger.ingest.load_file()


def test_ingest_no_config(small_example_ledger: FavaLedger) -> None:
    assert small_example_ledger.ingest.import_data() == []
    with pytest.raises(FavaAPIError):
        small_example_ledger.ingest.extract("import.csv", "import_name")


def test_ingest_examplefile(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    ingest_ledger = get_ledger("import")
    assert not ingest_ledger.ingest.errors

    files = ingest_ledger.ingest.import_data()
    assert len(files) == len(
        list(test_data_dir.iterdir())
    )  # all files in the test datafolder

    with pytest.raises(ImporterExtractError):
        ingest_ledger.ingest.extract(
            str(test_data_dir / "import.csv"),
            "<run_path>.TestImporterThatErrorsOnExtrac",
        )
    entries = ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestBeangulpImporterNoExtraction",
    )
    assert not entries

    entries = ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestImporter",
    )
    snapshot([serialise(e) for e in entries], json=True)
    assert len(entries) == 4
    assert entries[0].date == datetime.date(2017, 2, 12)
    assert isinstance(entries[0], Note)
    assert entries[0].comment == "Hinweis: Zinssatz auf 0,15% geändert"
    assert isinstance(entries[1], Transaction)
    assert entries[1].date == datetime.date(2017, 2, 13)
    assert (
        entries[1].narration
        == "Payment to Company XYZ REF: 31000161205-6944556-0000463"
    )
    assert not entries[1].postings[0].account
    assert entries[1].postings[0].units is not None
    assert entries[1].postings[0].units.number == 50.00
    assert entries[1].postings[0].units.currency == "EUR"
    assert entries[1].postings[1].account == "Assets:Checking"
    assert entries[1].postings[1].units is not None
    assert entries[1].postings[1].units.number == -50.00
    assert entries[1].postings[1].units.currency == "EUR"

    ingest_ledger.ingest.extract(
        str(test_data_dir / "import.csv"),
        "<run_path>.TestBeangulpImporter",
    )
    snapshot([serialise(e) for e in entries], json=True)


@pytest.mark.parametrize("hook_kind", ["function", "method", "object"])
@pytest.mark.parametrize(
    ("annotation", "tuple_length"),
    [
        pytest.param(None, 2, id="unannotated"),
        pytest.param("list[tuple[str, list]]", 2, id="legacy-string"),
        pytest.param(list[tuple[str, list[Any]]], 2, id="legacy-runtime"),
        pytest.param(list, 2, id="bare-list"),
        pytest.param(
            "list[tuple[str, list, str, Importer]]", 4, id="beangulp-string"
        ),
        pytest.param(
            list[tuple[str, list[Any], str, Importer]],
            4,
            id="beangulp-runtime",
        ),
    ],
)
def test_ingest_hook_annotations(
    test_data_dir: Path,
    get_ledger: GetFavaLedger,
    hook_kind: str,
    annotation: object,
    tuple_length: int,
) -> None:
    ledger = get_ledger("import")
    config = ledger.ingest.loaded_config
    assert config
    importer_name = "<run_path>.TestBeangulpImporter"
    filename = str(test_data_dir / "import.csv")
    calls = []

    def hook(
        extracted: HookOutput, existing: Sequence[Directive]
    ) -> HookOutput:
        calls.append(extracted)
        assert existing is ledger.all_entries
        assert len(extracted) == 1
        row = extracted[0]
        assert len(row) == tuple_length
        assert row[0] == filename
        if len(row) == 4:
            assert row[2] == "Assets:Checking"
            assert row[3] is config.importers[importer_name].importer
        assert len(row[1]) == 4
        row[1].pop()
        return extracted

    class Hook:
        def __call__(
            self, extracted: HookOutput, existing: Sequence[Directive]
        ) -> HookOutput:
            return hook(extracted, existing)

    # This module postpones annotations; assign runtime types explicitly to
    # exercise hooks defined without `from __future__ import annotations` too.
    annotations = {} if annotation is None else {"return": annotation}
    hook.__annotations__ = annotations
    Hook.__call__.__annotations__ = annotations
    callable_hook = Hook()
    hooks: dict[
        str, Callable[[HookOutput, Sequence[Directive]], HookOutput]
    ] = {
        "function": hook,
        "method": callable_hook.__call__,
        "object": callable_hook,
    }
    ledger.ingest.loaded_config = replace(config, hooks=[hooks[hook_kind]])

    entries = ledger.ingest.extract(filename, importer_name)
    assert len(calls) == 1
    assert len(entries) == 3


def test_filepath_in_primary_imports_folder(
    example_ledger: FavaLedger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", ["/test"])

    def _join(start: str, *args: str) -> Path:
        return Path(start).joinpath(*args).resolve()

    assert filepath_in_primary_imports_folder(
        "filename",
        example_ledger,
    ) == _join("/test", "filename")
    assert filepath_in_primary_imports_folder(
        "file/name",
        example_ledger,
    ) == _join("/test", "file name")
    assert filepath_in_primary_imports_folder(
        "/../file/name",
        example_ledger,
    ) == _join("/test", " .. file name")

    monkeypatch.setattr(example_ledger.fava_options, "import_dirs", [])
    with pytest.raises(FavaAPIError):
        filepath_in_primary_imports_folder("filename", example_ledger)
