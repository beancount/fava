"""JSON API.

This module contains the url endpoints of the JSON API that is used by the web
interface for asynchronous functionality.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from functools import wraps
from http import HTTPStatus
from inspect import Parameter
from inspect import signature
from pathlib import Path
from pprint import pformat
from string import Template
from typing import TYPE_CHECKING
from typing import TypeVar

import msgspec
from flask import Blueprint
from flask import get_template_attribute
from flask import jsonify
from flask import request
from flask_babel import gettext
from msgspec import Struct
from msgspec.structs import astuple

from fava import _structs  # noqa: TC001 - needed for msgspec
from fava.beans.abc import Document
from fava.beans.abc import Event
from fava.context import g
from fava.core import EntryNotFoundForHashError
from fava.core.conversion import UNITS
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.core.fava_options import All_OPTS
from fava.core.file import GeneratedEntryError
from fava.core.file import get_entry_slice
from fava.core.filters import FilterError
from fava.core.group_entries import group_entries_by_type
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.core.misc import align
from fava.helpers import FavaAPIError
from fava.internal_api import ChartApi
from fava.internal_api import get_errors
from fava.internal_api import get_ledger_data
from fava.serialisation import deserialise
from fava.serialisation import serialise

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Mapping
    from collections.abc import Sequence
    from datetime import date
    from decimal import Decimal

    from flask.wrappers import Response
    from werkzeug.datastructures import FileStorage

    from fava.core.ingest import FileImporters
    from fava.core.inventory import SimpleCounterInventory
    from fava.core.query import QueryResultTable
    from fava.core.query import QueryResultText
    from fava.core.tree import SerialisedTreeNode
    from fava.internal_api import ChartData
    from fava.util.date import DateRange


json_api = Blueprint("json_api", __name__)
log = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def _which(command: str) -> str | None:
    """Resolve executable path with an LRU cache."""
    return shutil.which(command)


class ErrorResponse(Struct, frozen=True):
    """Error response object structure."""

    error: str


class SuccessResponse(Struct, frozen=True):
    """Response structure."""

    data: object
    mtime: str


def json_err(msg: str, status: HTTPStatus) -> Response:
    """Jsonify the error message."""
    res = jsonify(ErrorResponse(msg))
    res.status = status
    return res


class FavaJSONAPIError(ABC, FavaAPIError):
    """An error with a HTTPStatus."""

    @property
    @abstractmethod
    def status(self) -> HTTPStatus:
        """HTTP status that should be used for the response."""


class ValidationError(FavaJSONAPIError):
    """Validation of data failed."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid API request: {reason}")


class InvalidJsonRequestError(ValidationError):
    """Invalid JSON body."""

    def __init__(self) -> None:
        super().__init__(self.__doc__ or "")


class NotFoundError(FavaJSONAPIError):
    """Not found."""

    status = HTTPStatus.NOT_FOUND


class TargetPathAlreadyExistsError(FavaJSONAPIError):
    """The given path already exists."""

    status = HTTPStatus.CONFLICT

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} already exists.")


class DocumentDirectoryMissingError(FavaJSONAPIError):
    """You need to set a documents folder."""

    status = HTTPStatus.UNPROCESSABLE_ENTITY


class NoFileUploadedError(FavaJSONAPIError):
    """No file uploaded."""

    status = HTTPStatus.BAD_REQUEST


class UploadedFileIsMissingFilenameError(FavaJSONAPIError):
    """Uploaded file is missing filename."""

    status = HTTPStatus.BAD_REQUEST


class NotAValidDocumentOrImportFileError(FavaJSONAPIError):
    """Not valid document or import file."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self, filename: str) -> None:
        super().__init__(f"Not valid document or import file: '{filename}'.")


class NotAFileError(FavaJSONAPIError):
    """Not a file."""

    status = HTTPStatus.UNPROCESSABLE_ENTITY

    def __init__(self, filename: str) -> None:
        super().__init__(f"Not a file: '{filename}'")


class NotASourceFileError(FavaJSONAPIError):
    """The given path is not a Beancount source file."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self, filename: str) -> None:
        super().__init__(f"Not a Beancount source file: '{filename}'.")


class ExternalEditorCommandMissingError(FavaJSONAPIError):
    """External editor command not configured."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self) -> None:
        super().__init__("No external editor command configured.")


class ExternalEditorCommandTemplateError(FavaJSONAPIError):
    """External editor command template invalid."""

    status = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid external editor command: {message}")


class ExternalEditorCommandExecutionError(FavaJSONAPIError):
    """Executing the external editor command failed."""

    status = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(f"Failed to run external editor command: {message}.")


@json_api.errorhandler(FavaAPIError)
def _(error: FavaAPIError) -> Response:
    log.error("Encountered FavaAPIError.", exc_info=error)
    return json_err(error.message, HTTPStatus.INTERNAL_SERVER_ERROR)


@json_api.errorhandler(FavaJSONAPIError)
def _(error: FavaJSONAPIError) -> Response:
    return json_err(error.message, error.status)


@json_api.errorhandler(FilterError)
def _(error: FilterError) -> Response:
    return json_err(error.message, HTTPStatus.BAD_REQUEST)


@json_api.errorhandler(OSError)
def _(error: OSError) -> Response:  # pragma: no cover
    log.error("Encountered OSError.", exc_info=error)
    return json_err(error.strerror or "", HTTPStatus.INTERNAL_SERVER_ERROR)


@json_api.errorhandler(EntryNotFoundForHashError)
def _(error: EntryNotFoundForHashError) -> Response:
    return json_err(error.message, HTTPStatus.NOT_FOUND)


@json_api.errorhandler(GeneratedEntryError)
def _(error: GeneratedEntryError) -> Response:
    return json_err(error.message, HTTPStatus.UNPROCESSABLE_ENTITY)


def _build_param_struct(func: Callable[..., object]) -> type[Struct] | None:
    """Build a msgspec Struct type matching a function's parameters."""
    struct_fields = []
    for param in signature(func).parameters.values():
        assert param.kind == Parameter.POSITIONAL_OR_KEYWORD, (  # noqa: S101
            f"Param {param.name} should be positional"
        )
        struct_fields.append(
            (param.name, param.annotation)
            if param.default is Parameter.empty
            else (param.name, param.annotation, param.default)
        )

    if not struct_fields:
        return None

    return msgspec.defstruct(f"{func.__name__}_params", struct_fields)  # ty:ignore[unresolved-attribute]


def build_json_body_decoder(
    func: Callable[..., object],
) -> Callable[[bytes], Sequence[object]] | None:
    """Build a msgspec-typed decoder for the JSON body of an endpoint."""
    param_struct = _build_param_struct(func)
    if param_struct is None:
        return None
    decoder = msgspec.json.Decoder(param_struct)

    def decode(data: bytes) -> Sequence[object]:
        try:
            return astuple(decoder.decode(data))
        except msgspec.ValidationError as error:
            raise ValidationError(str(error)) from error
        except msgspec.DecodeError as error:
            raise InvalidJsonRequestError from error

    return decode


def build_query_string_decoder(
    func: Callable[..., object],
) -> Callable[[Mapping[str, str]], Sequence[object]] | None:
    """Build a msgspec-typed decoder for an endpoint's query string."""
    param_struct = _build_param_struct(func)
    if param_struct is None:
        return None

    def decode(args: Mapping[str, str]) -> Sequence[object]:
        try:
            return astuple(
                msgspec.convert(args, type=param_struct, strict=False)
            )
        except msgspec.ValidationError as error:
            raise ValidationError(str(error)) from error

    return decode


T = TypeVar("T")


def validate_form(t: type[T]) -> T:
    """Validate the provided form fields to match the passed type."""
    try:
        return msgspec.convert(dict(request.form), t)
    except msgspec.ValidationError as error:
        raise ValidationError(str(error)) from error


def validate_file() -> tuple[FileStorage, str]:
    """Validate the form request contains a file with filename."""
    upload = request.files.get("file", None)

    if upload is None:
        raise NoFileUploadedError
    if not upload.filename:
        raise UploadedFileIsMissingFilenameError

    return (upload, upload.filename)


def api_endpoint(func: Callable[..., object]) -> Callable[[], Response]:
    """Register an API endpoint.

    The part of the function name up to the first underscore determines
    the accepted HTTP method. For GET and DELETE endpoints, the function
    parameters are converted from the URL query string; for PUT endpoints,
    they are decoded from the JSON request body. Both use a msgspec Struct
    generated from the function's parameters for the typed validation.
    """
    method, _, name = func.__name__.partition("_")  # ty:ignore[unresolved-attribute]
    assert method in {"get", "delete", "put"}, (  # noqa: S101
        f"Invalid endpoint function name: {func.__name__}"  # ty: ignore[unresolved-attribute]
    )

    if method == "put":
        decode_body = build_json_body_decoder(func)

        def get_args() -> Sequence[object]:
            return decode_body(request.get_data()) if decode_body else []
    else:
        decode_args = build_query_string_decoder(func)

        def get_args() -> Sequence[object]:
            return decode_args(dict(request.args)) if decode_args else []

    @json_api.route(f"/{name}", methods=[method])
    @wraps(func)
    def _wrapper() -> Response:
        return jsonify(SuccessResponse(func(*get_args()), str(g.ledger.mtime)))

    return _wrapper


@api_endpoint
def get_changed() -> bool:
    """Check for file changes."""
    return g.ledger.changed()


api_endpoint(get_errors)
api_endpoint(get_ledger_data)


@api_endpoint
def get_payee_accounts(payee: str) -> Sequence[str]:
    """Rank accounts for the given payee."""
    return g.ledger.attributes.payee_accounts(payee)


@api_endpoint
def get_query(query_string: str) -> QueryResultTable | QueryResultText:
    """Run a Beancount query."""
    return g.ledger.query_shell.execute_query_serialised(
        g.filtered.entries_with_all_prices, query_string
    )


@api_endpoint
def get_extract(filename: str, importer: str) -> Sequence[object]:
    """Extract entries using the ingest framework."""
    g.ledger.changed()
    entries = g.ledger.ingest.extract(filename, importer)
    return list(map(serialise, entries))


class Context(Struct, frozen=True):
    """Context for an entry."""

    entry: object
    balances_before: Mapping[str, Sequence[str]] | None
    balances_after: Mapping[str, Sequence[str]] | None


@api_endpoint
def get_context(entry_hash: str) -> Context:
    """Entry context."""
    entry, before, after = g.ledger.context(entry_hash)
    return Context(serialise(entry), before, after)


class SourceSlice(Struct, frozen=True):
    """Source slice for an entry."""

    sha256sum: str
    slice: str


@api_endpoint
def get_source_slice(entry_hash: str) -> SourceSlice:
    """Entry slice."""
    entry = g.ledger.get_entry(entry_hash)
    source_slice, sha256sum = get_entry_slice(entry)
    return SourceSlice(sha256sum, source_slice)


@api_endpoint
def put_move(account: str, new_name: str, filename: str) -> str:
    """Move a document."""
    if not g.ledger.options["documents"]:
        raise DocumentDirectoryMissingError

    new_path = filepath_in_document_folder(
        g.ledger.options["documents"][0], account, new_name, g.ledger
    )
    file_path = Path(filename)

    if not file_path.is_file():
        raise NotAFileError(filename)
    if not is_document_or_import_file(filename, g.ledger):
        raise NotAValidDocumentOrImportFileError(filename)
    if new_path.exists():
        raise TargetPathAlreadyExistsError(new_path)

    new_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(filename, new_path)

    return f"Moved {filename} to {new_path}."


@api_endpoint
def get_payee_transaction(payee: str) -> object:
    """Last transaction for the given payee."""
    entry = g.ledger.attributes.payee_transaction(payee)
    return serialise(entry) if entry else None


@api_endpoint
def get_narration_transaction(narration: str) -> object:
    """Last transaction for the given narration."""
    entry = g.ledger.attributes.narration_transaction(narration)
    return serialise(entry) if entry else None


@api_endpoint
def get_narrations() -> Sequence[str]:
    """List of all narrations in the ledger."""
    return g.ledger.attributes.narrations


class SourceFile(Struct, frozen=True):
    """Source slice for an entry."""

    file_path: str
    sha256sum: str
    source: str


@api_endpoint
def get_source(filename: str = "") -> SourceFile:
    """Load one of the source files."""
    file_path = (
        filename
        or g.ledger.fava_options.default_file
        or g.ledger.beancount_file_path
    )
    source, sha256sum = g.ledger.file.get_source(Path(file_path))
    return SourceFile(file_path=file_path, sha256sum=sha256sum, source=source)


@api_endpoint
def put_open_in_editor(file_path: str, line: str) -> str:
    """Execute the configured external editor command."""
    command_template = None
    if g.ledger.project_config is not None:
        command_template = g.ledger.project_config.external_editor_command
    if command_template is None:
        raise ExternalEditorCommandMissingError

    resolved_path = Path(file_path).resolve()
    include_paths = {
        Path(include).resolve() for include in g.ledger.options["include"]
    }
    if resolved_path not in include_paths:
        raise NotASourceFileError(file_path)
    if not resolved_path.is_file():
        raise NotAFileError(file_path)

    try:
        line_num = int(line)
    except ValueError as err:
        msg = "line must be an integer"
        raise ExternalEditorCommandTemplateError(msg) from err

    if not command_template:
        msg = "command is empty"
        raise ExternalEditorCommandTemplateError(msg)

    command, *args = command_template
    if not command:
        msg = "command is empty"
        raise ExternalEditorCommandTemplateError(msg)

    command_abs = _which(command)

    if command_abs is None:  # pragma: no cover - depends on environment
        msg = f"{command} not found in PATH"
        raise ExternalEditorCommandExecutionError(msg)

    try:
        args = [
            Template(part).substitute(
                file=str(resolved_path),
                line=str(line_num),
            )
            for part in args
        ]
    except KeyError as err:
        missing = err.args[0] if err.args else "unknown"
        msg = f"missing variable '{missing}'"
        raise ExternalEditorCommandTemplateError(msg) from err
    except ValueError as err:
        raise ExternalEditorCommandTemplateError(str(err)) from err

    try:
        subprocess.check_call([command_abs, *args])
    except (
        subprocess.CalledProcessError
    ) as err:  # pragma: no cover - depends on environment
        log.exception("Failed to run external editor command")
        message = err.stderr or str(err)
        raise ExternalEditorCommandExecutionError(message) from err
    except OSError as err:  # pragma: no cover - depends on environment
        log.exception("Failed to run external editor command")
        message = err.strerror or str(err)
        raise ExternalEditorCommandExecutionError(message) from err

    return f"Launching: {' '.join(args)}"


@api_endpoint
def put_source(file_path: str, source: str, sha256sum: str) -> str:
    """Write one of the source files and return the updated sha256sum."""
    return g.ledger.file.set_source(Path(file_path), source, sha256sum)


@api_endpoint
def put_source_slice(entry_hash: str, source: str, sha256sum: str) -> str:
    """Write an entry source slice and return the updated sha256sum."""
    return g.ledger.file.save_entry_slice(entry_hash, source, sha256sum)


@api_endpoint
def delete_source_slice(entry_hash: str, sha256sum: str) -> str:
    """Delete an entry source slice."""
    g.ledger.file.delete_entry_slice(entry_hash, sha256sum)
    return f"Deleted entry {entry_hash}."


@api_endpoint
def put_format_source(source: str) -> str:
    """Format beancount file."""
    return align(source, g.ledger.fava_options.currency_column)


class FileDoesNotExistError(FavaJSONAPIError):
    """The given file does not exist."""

    status = HTTPStatus.NOT_FOUND

    def __init__(self, filename: str) -> None:
        super().__init__(f"{filename} does not exist.")


@api_endpoint
def delete_document(filename: str) -> str:
    """Delete a document."""
    if not is_document_or_import_file(filename, g.ledger):
        raise NotAValidDocumentOrImportFileError(filename)

    file_path = Path(filename)
    if not file_path.exists():
        raise FileDoesNotExistError(filename)

    file_path.unlink()
    return f"Deleted {filename}."


class AddDocumentForm(Struct, frozen=True):
    """Required form fields when adding a document."""

    folder: str
    account: str
    hash: str = ""


@api_endpoint
def put_add_document() -> str:
    """Upload a document."""
    if not g.ledger.options["documents"]:
        raise DocumentDirectoryMissingError

    upload, name = validate_file()
    form = validate_form(AddDocumentForm)
    filepath = filepath_in_document_folder(
        form.folder, form.account, name, g.ledger
    )

    if filepath.exists():
        raise TargetPathAlreadyExistsError(filepath)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    upload.save(filepath)

    if form.hash:
        g.ledger.file.insert_metadata(form.hash, "document", filepath.name)
    return f"Uploaded to {filepath}"


@api_endpoint
def put_attach_document(filename: str, entry_hash: str) -> str:
    """Attach a document to an entry."""
    g.ledger.file.insert_metadata(entry_hash, "document", filename)
    return f"Attached '{filename}' to entry."


@api_endpoint
def put_add_entries(
    entries: list[_structs.Balance | _structs.Note | _structs.Transaction],
) -> str:
    """Add multiple entries."""
    g.ledger.file.insert_entries([deserialise(entry) for entry in entries])

    return f"Stored {len(entries)} entries."


@api_endpoint
def put_upload_import_file() -> str:
    """Upload a file for importing."""
    upload, name = validate_file()
    filepath = filepath_in_primary_imports_folder(name, g.ledger)

    if filepath.exists():
        raise TargetPathAlreadyExistsError(filepath)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    upload.save(filepath)

    return f"Uploaded to {filepath}"


########################################################################
# Reports


@api_endpoint
def get_journal() -> Sequence[object]:
    """Get all (filtered) entries."""
    g.ledger.changed()
    return [serialise(e) for e in g.filtered.entries]


class JournalPage(Struct, frozen=True):
    """A rendered journal page."""

    page: int
    total_pages: int
    journal: str


@api_endpoint
def get_journal_page(page: int, order: str) -> JournalPage:
    """Get the HTML contents for a Journal page."""
    journal_table_contents = get_template_attribute(
        "_journal_table.html", "journal_table_contents"
    )
    if page == 1:
        g.ledger.changed()
    journal_page = g.filtered.paginate_journal(
        page, order="asc" if order == "asc" else "desc"
    )
    if journal_page is None:
        raise NotFoundError
    return JournalPage(
        page=page,
        total_pages=journal_page.total_pages,
        journal=journal_table_contents(journal_page.entries),
    )


@api_endpoint
def get_events() -> Sequence[object]:
    """Get all (filtered) events."""
    g.ledger.changed()
    return [serialise(e) for e in g.filtered.entries if isinstance(e, Event)]


@api_endpoint
def get_imports() -> Sequence[FileImporters]:
    """Get a list of the importable files."""
    g.ledger.changed()
    return g.ledger.ingest.import_data()


@api_endpoint
def get_documents() -> Sequence[object]:
    """Get all (filtered) documents."""
    g.ledger.changed()
    return [
        serialise(e) for e in g.filtered.entries if isinstance(e, Document)
    ]


class Options(Struct, frozen=True):
    """Fava and Beancount options as strings."""

    fava_options: Mapping[str, str]
    beancount_options: Mapping[str, str]


@api_endpoint
def get_options() -> Options:
    """Get all options, rendered to strings for displaying in the frontend."""
    g.ledger.changed()

    fava_options = g.ledger.fava_options
    pprinted_fava_options = {
        name.replace("_", "-"): pformat(getattr(fava_options, name))
        for name in All_OPTS
    }
    return Options(
        pprinted_fava_options,
        {key: str(value) for key, value in g.ledger.options.items()},
    )


class HelpPage(Struct, frozen=True):
    """A rendered help page and the list of all help pages."""

    html: str
    pages: Sequence[tuple[str, str]]


@api_endpoint
def get_help(page_slug: str) -> HelpPage:
    """Get one of Fava's help pages, rendered to HTML."""
    from fava.help import HELP_PAGES
    from fava.help import render_help_page

    html = render_help_page(page_slug)
    if html is None:
        raise NotFoundError
    return HelpPage(html, list(HELP_PAGES.items()))


class CommodityPairWithPrices(Struct, frozen=True):
    """A pair of commodities and prices for them."""

    base: str
    quote: str
    prices: Sequence[tuple[date, Decimal]]


@api_endpoint
def get_commodities() -> Sequence[CommodityPairWithPrices]:
    """Get the prices for all commodity pairs."""
    g.ledger.changed()
    ret = []
    for base, quote in g.ledger.commodity_pairs():
        prices = g.filtered.prices(base, quote)
        if prices:
            ret.append(CommodityPairWithPrices(base, quote, prices))

    return ret


class TreeReport(Struct, frozen=True):
    """Data for the tree reports."""

    date_range: DateRange | None
    charts: Sequence[ChartData]
    trees: Sequence[SerialisedTreeNode]


@api_endpoint
def get_income_statement() -> TreeReport:
    """Get the data for the income statement."""
    g.ledger.changed()
    options = g.ledger.options
    invert = g.ledger.fava_options.invert_income_liabilities_equity

    charts = [
        ChartApi.interval_totals(
            g.interval,
            (options["name_income"], options["name_expenses"]),
            label=gettext("Net Profit"),
            invert=invert,
        ),
        ChartApi.interval_totals(
            g.interval,
            options["name_income"],
            label=f"{gettext('Income')} ({g.interval.label})",
            invert=invert,
        ),
        ChartApi.interval_totals(
            g.interval,
            options["name_expenses"],
            label=f"{gettext('Expenses')} ({g.interval.label})",
        ),
    ]
    root_tree = g.filtered.root_tree
    trees = [
        root_tree.get(options["name_income"]),
        root_tree.net_profit(options, gettext("Net Profit")),
        root_tree.get(options["name_expenses"]),
    ]

    return TreeReport(
        g.filtered.date_range,
        charts,
        trees=[tree.serialise_with_context() for tree in trees],
    )


@api_endpoint
def get_balance_sheet() -> TreeReport:
    """Get the data for the balance sheet."""
    g.ledger.changed()
    options = g.ledger.options

    charts = [ChartApi.net_worth()]
    root_tree_closed = g.filtered.root_tree_closed
    trees = [
        root_tree_closed.get(options["name_assets"]),
        root_tree_closed.get(options["name_liabilities"]),
        root_tree_closed.get(options["name_equity"]),
    ]

    return TreeReport(
        g.filtered.date_range,
        charts,
        trees=[tree.serialise_with_context() for tree in trees],
    )


@api_endpoint
def get_trial_balance() -> TreeReport:
    """Get the data for the trial balance."""
    g.ledger.changed()

    trees = [g.filtered.root_tree.get("")]

    return TreeReport(
        g.filtered.date_range,
        charts=[],
        trees=[tree.serialise_with_context() for tree in trees],
    )


class AccountBudget(Struct, frozen=True):
    """Budgets for an account."""

    budget: Mapping[str, Decimal]
    budget_children: Mapping[str, Decimal]


class AccountReportJournal(Struct, frozen=True):
    """Data for the journal account report."""

    charts: Sequence[ChartData]
    journal: str


class AccountReportTree(Struct, frozen=True):
    """Data for the tree account reports."""

    charts: Sequence[ChartData]
    interval_balances: Sequence[SerialisedTreeNode]
    budgets: Mapping[str, Sequence[AccountBudget]]
    dates: Sequence[DateRange]


@api_endpoint
def get_account_report(
    a: str = "", r: str = ""
) -> AccountReportJournal | AccountReportTree:
    """Get the data for the account report."""
    g.ledger.changed()

    charts = [
        ChartApi.account_balance(a),
        ChartApi.interval_totals(
            g.interval,
            a,
            label=gettext("Changes"),
        ),
    ]

    if r in {"changes", "balances"}:
        accumulate = r == "balances"
        interval_balances, dates = g.ledger.interval_balances(
            g.filtered, g.interval, a, accumulate=accumulate
        )
        if not dates:
            return AccountReportTree(
                charts, interval_balances=[], budgets={}, dates=[]
            )

        all_accounts = (
            interval_balances[0].accounts if interval_balances else []
        )
        budget_accounts = [acc for acc in all_accounts if acc.startswith(a)]
        budgets_mod = g.ledger.budgets
        first_date_range = dates[-1]
        budgets = {
            account: [
                AccountBudget(
                    budgets_mod.calculate(
                        account,
                        (first_date_range if accumulate else date_range).begin,
                        date_range.end,
                    ),
                    budgets_mod.calculate_children(
                        account,
                        (first_date_range if accumulate else date_range).begin,
                        date_range.end,
                    ),
                )
                for date_range in dates
            ]
            for account in budget_accounts
        }

        return AccountReportTree(
            charts,
            interval_balances=[
                tree.get(a).serialise(
                    g.conv,
                    g.ledger.prices,
                    date_range.end_inclusive,
                    with_cost=False,
                )
                for tree, date_range in zip(
                    interval_balances, dates, strict=True
                )
            ],
            dates=dates,
            budgets=budgets,
        )

    journal_table_contents = get_template_attribute(
        "_journal_table.html", "journal_table_contents"
    )
    entries = reversed(
        g.ledger.account_journal(
            g.filtered,
            a,
            g.conv,
            with_children=g.ledger.fava_options.account_journal_include_children,
        )
    )
    return AccountReportJournal(
        charts,
        journal=journal_table_contents(entries, show_change_and_balance=True),
    )


class Statistics(Struct, frozen=True):
    """Data for the statistics report."""

    all_balance_directives: str
    balances: Mapping[str, SimpleCounterInventory]
    entries_by_type: Mapping[str, int]


@api_endpoint
def get_statistics() -> Statistics:
    """Get the data for the statistics report."""
    g.ledger.changed()

    entries_by_type = group_entries_by_type(g.filtered.entries).count_by_type()

    balances = {
        account_name: UNITS.apply(node.balance)
        for account_name, node in g.filtered.root_tree.items()
    }

    return Statistics(
        all_balance_directives=g.ledger.accounts.all_balance_directives(),
        balances=balances,
        entries_by_type=entries_by_type,
    )
