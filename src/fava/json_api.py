"""JSON API.

This module contains the url endpoints of the JSON API that is used by the web
interface for asynchronous functionality.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from functools import wraps
from inspect import Parameter
from inspect import signature
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Mapping
from typing import TYPE_CHECKING

from flask import Blueprint
from flask import get_template_attribute
from flask import jsonify
from flask import request
from flask_babel import gettext  # type: ignore[import-untyped]

from fava.beans.abc import Document
from fava.beans.abc import Event
from fava.context import g
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.core.misc import align
from fava.helpers import FavaAPIError
from fava.internal_api import ChartApi
from fava.internal_api import get_errors
from fava.internal_api import get_ledger_data
from fava.serialisation import deserialise
from fava.serialisation import serialise

if TYPE_CHECKING:  # pragma: no cover
    from datetime import date
    from decimal import Decimal

    from flask.wrappers import Response

    from fava.core.ingest import FileImporters
    from fava.core.query_shell import QueryResultTable
    from fava.core.query_shell import QueryResultText
    from fava.core.tree import SerialisedTreeNode
    from fava.internal_api import ChartData
    from fava.util.date import DateRange


json_api = Blueprint("json_api", __name__)


class ValidationError(Exception):
    """Validation of data failed."""


class MissingParameterValidationError(ValidationError):
    """Validation failed due to missing parameter."""

    def __init__(self, param: str) -> None:
        super().__init__(f"Parameter `{param}` is missing.")


class IncorrectTypeValidationError(ValidationError):
    """Validation failed due to incorrect type of parameter."""

    def __init__(self, param: str, expected: type) -> None:
        super().__init__(
            f"Parameter `{param}` of incorrect type - expected {expected}.",
        )


def json_err(msg: str) -> Response:
    """Jsonify the error message."""
    return jsonify({"success": False, "error": msg})


def json_success(data: Any) -> Response:
    """Jsonify the response."""
    return jsonify(
        {"success": True, "data": data, "mtime": str(g.ledger.mtime)},
    )


@json_api.errorhandler(FavaAPIError)
def _json_api_exception(error: FavaAPIError) -> Response:
    return json_err(error.message)


@json_api.errorhandler(OSError)
def _json_api_oserror(error: OSError) -> Response:
    return json_err(error.strerror)


@json_api.errorhandler(ValidationError)
def _json_api_validation_error(error: ValidationError) -> Response:
    return json_err(f"Invalid API request: {error!s}")


def validate_func_arguments(
    func: Callable[..., Any],
) -> Callable[[Mapping[str, str]], list[str]] | None:
    """Validate arguments for a function.

    This currently only works for strings and lists (but only does a shallow
    validation for lists).

    Args:
        func: The function to check parameters for.

    Returns:
        A function, which takes a Mapping and tries to construct a list of
        positional parameters for the given function or None if the function
        has no parameters.
    """
    sig = signature(func)
    params: list[tuple[str, Any]] = []
    for param in sig.parameters.values():
        if param.annotation not in {"str", "list[Any]"}:  # pragma: no cover
            msg = (f"Type of param {param.name} needs to str or list",)
            raise ValueError(msg)
        if param.kind != Parameter.POSITIONAL_OR_KEYWORD:  # pragma: no cover
            msg2 = f"Param {param.name} should be positional"
            raise ValueError(msg2)
        params.append((param.name, str if param.annotation == "str" else list))

    if not params:
        return None

    def validator(mapping: Mapping[str, str]) -> list[str]:
        args: list[str] = []
        for param, type_ in params:
            val = mapping.get(param, None)
            if val is None:
                raise MissingParameterValidationError(param)
            if not isinstance(val, type_):
                raise IncorrectTypeValidationError(param, type_)
            args.append(val)
        return args

    return validator


def api_endpoint(func: Callable[..., Any]) -> Callable[[], Response]:
    """Register an API endpoint.

    The part of the function name up to the first underscore determines
    the accepted HTTP method. For GET and DELETE endpoints, the function
    parameters are extracted from the URL query string and passed to the
    decorated endpoint handler.
    """
    method, _, name = func.__name__.partition("_")
    if method not in {"get", "delete", "put"}:  # pragma: no cover
        msg = f"Invalid endpoint function name: {func.__name__}"
        raise ValueError(msg)
    validator = validate_func_arguments(func)

    @json_api.route(f"/{name}", methods=[method])
    @wraps(func)
    def _wrapper() -> Response:
        if validator is not None:
            if method == "put":
                request_json = request.get_json(silent=True)
                if request_json is None:
                    msg = "Invalid JSON request."
                    raise FavaAPIError(msg)
                data = request_json
            else:
                data = request.args
            res = func(*validator(data))
        else:
            res = func()
        return json_success(res)

    return _wrapper


class TargetPathAlreadyExistsError(FavaAPIError):
    """The given path already exists."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} already exists.")


class DocumentDirectoryMissingError(FavaAPIError):
    """No document directory was specified."""

    def __init__(self) -> None:
        super().__init__("You need to set a documents folder.")


class NoFileUploadedError(FavaAPIError):
    """No file uploaded."""

    def __init__(self) -> None:
        super().__init__("No file uploaded.")


class UploadedFileIsMissingFilenameError(FavaAPIError):
    """Uploaded file is missing filename."""

    def __init__(self) -> None:
        super().__init__("Uploaded file is missing filename.")


class NotAValidDocumentOrImportFileError(FavaAPIError):
    """Not valid document or import file."""

    def __init__(self, filename: str) -> None:
        super().__init__(f"Not valid document or import file: '{filename}'.")


class NotAFileError(FavaAPIError):
    """Not a file."""

    def __init__(self, filename: str) -> None:
        super().__init__(f"Not a file: '{filename}'")


@api_endpoint
def get_changed() -> bool:
    """Check for file changes."""
    return g.ledger.changed()


api_endpoint(get_errors)
api_endpoint(get_ledger_data)


@api_endpoint
def get_payee_accounts(payee: str) -> list[str]:
    """Rank accounts for the given payee."""
    return g.ledger.attributes.payee_accounts(payee)


@api_endpoint
def get_query(query_string: str) -> QueryResultTable | QueryResultText:
    """Run a Beancount query."""
    return g.ledger.query_shell.execute_query_serialised(
        g.filtered.entries,
        query_string,
    )


@api_endpoint
def get_extract(filename: str, importer: str) -> list[Any]:
    """Extract entries using the ingest framework."""
    entries = g.ledger.ingest.extract(filename, importer)
    return list(map(serialise, entries))


@dataclass(frozen=True)
class Context:
    """Context for an entry."""

    entry: Any
    balances_before: dict[str, list[str]] | None
    balances_after: dict[str, list[str]] | None
    sha256sum: str
    slice: str


@api_endpoint
def get_context(entry_hash: str) -> Context:
    """Entry context."""
    entry, before, after, slice_, sha256sum = g.ledger.context(entry_hash)
    return Context(serialise(entry), before, after, sha256sum, slice_)


@api_endpoint
def get_move(account: str, new_name: str, filename: str) -> str:
    """Move a file."""
    if not g.ledger.options["documents"]:
        raise DocumentDirectoryMissingError

    new_path = filepath_in_document_folder(
        g.ledger.options["documents"][0],
        account,
        new_name,
        g.ledger,
    )
    file_path = Path(filename)

    if not file_path.is_file():
        raise NotAFileError(filename)
    if new_path.exists():
        raise TargetPathAlreadyExistsError(new_path)

    if not new_path.parent.exists():
        new_path.parent.mkdir(parents=True)
    shutil.move(filename, new_path)

    return f"Moved {filename} to {new_path}."


@api_endpoint
def get_payee_transaction(payee: str) -> Any:
    """Last transaction for the given payee."""
    entry = g.ledger.attributes.payee_transaction(payee)
    return serialise(entry) if entry else None


@api_endpoint
def get_source(filename: str) -> dict[str, str]:
    """Load one of the source files."""
    file_path = (
        filename
        or g.ledger.fava_options.default_file
        or g.ledger.beancount_file_path
    )
    source, sha256sum = g.ledger.file.get_source(Path(file_path))
    return {"source": source, "sha256sum": sha256sum, "file_path": file_path}


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


class FileDoesNotExistError(FavaAPIError):
    """The given file does not exist."""

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


@api_endpoint
def put_add_document() -> str:
    """Upload a document."""
    if not g.ledger.options["documents"]:
        raise DocumentDirectoryMissingError

    upload = request.files.get("file", None)

    if not upload:
        raise NoFileUploadedError
    if not upload.filename:
        raise UploadedFileIsMissingFilenameError

    filepath = filepath_in_document_folder(
        request.form["folder"],
        request.form["account"],
        upload.filename,
        g.ledger,
    )

    if filepath.exists():
        raise TargetPathAlreadyExistsError(filepath)

    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)

    upload.save(filepath)

    if request.form.get("hash"):
        g.ledger.file.insert_metadata(
            request.form["hash"],
            "document",
            filepath.name,
        )
    return f"Uploaded to {filepath}"


@api_endpoint
def put_attach_document(filename: str, entry_hash: str) -> str:
    """Attach a document to an entry."""
    g.ledger.file.insert_metadata(entry_hash, "document", filename)
    return f"Attached '{filename}' to entry."


@api_endpoint
def put_add_entries(entries: list[Any]) -> str:
    """Add multiple entries."""
    try:
        entries = [deserialise(entry) for entry in entries]
    except KeyError as error:
        msg = f"KeyError: {error}"
        raise FavaAPIError(msg) from error

    g.ledger.file.insert_entries(entries)

    return f"Stored {len(entries)} entries."


@api_endpoint
def put_upload_import_file() -> str:
    """Upload a file for importing."""
    upload = request.files.get("file", None)

    if not upload:
        raise NoFileUploadedError
    if not upload.filename:
        raise UploadedFileIsMissingFilenameError
    filepath = filepath_in_primary_imports_folder(upload.filename, g.ledger)

    if filepath.exists():
        raise TargetPathAlreadyExistsError(filepath)

    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)

    upload.save(filepath)

    return f"Uploaded to {filepath}"


########################################################################
# Reports


@api_endpoint
def get_events() -> list[Event]:
    """Get all (filtered) events."""
    g.ledger.changed()
    return [serialise(e) for e in g.filtered.entries if isinstance(e, Event)]


@api_endpoint
def get_imports() -> list[FileImporters]:
    """Get a list of the importable files."""
    g.ledger.changed()
    return g.ledger.ingest.import_data()


@api_endpoint
def get_documents() -> list[Document]:
    """Get all (filtered) documents."""
    g.ledger.changed()
    return [
        serialise(e) for e in g.filtered.entries if isinstance(e, Document)
    ]


@dataclass(frozen=True)
class CommodityPairWithPrices:
    """A pair of commodities and prices for them."""

    base: str
    quote: str
    prices: list[tuple[date, Decimal]]


@api_endpoint
def get_commodities() -> list[CommodityPairWithPrices]:
    """Get the prices for all commodity pairs."""
    g.ledger.changed()
    ret = []
    for base, quote in g.ledger.commodity_pairs():
        prices = g.filtered.prices(base, quote)
        if prices:
            ret.append(CommodityPairWithPrices(base, quote, prices))

    return ret


@dataclass(frozen=True)
class TreeReport:
    """Data for the tree reports."""

    date_range: DateRange | None
    charts: list[ChartData]
    trees: list[SerialisedTreeNode]


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
        ChartApi.hierarchy(options["name_income"]),
        ChartApi.hierarchy(options["name_expenses"]),
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

    charts = [
        ChartApi.net_worth(),
        ChartApi.hierarchy(options["name_assets"]),
        ChartApi.hierarchy(options["name_liabilities"]),
        ChartApi.hierarchy(options["name_equity"]),
    ]
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
    options = g.ledger.options

    charts = [
        ChartApi.hierarchy(options["name_income"]),
        ChartApi.hierarchy(options["name_expenses"]),
        ChartApi.hierarchy(options["name_assets"]),
        ChartApi.hierarchy(options["name_liabilities"]),
        ChartApi.hierarchy(options["name_equity"]),
    ]
    trees = [g.filtered.root_tree.get("")]

    return TreeReport(
        g.filtered.date_range,
        charts,
        trees=[tree.serialise_with_context() for tree in trees],
    )


@dataclass(frozen=True)
class AccountBudget:
    """Budgets for an account."""

    budget: dict[str, Decimal]
    budget_children: dict[str, Decimal]


@dataclass(frozen=True)
class AccountReportJournal:
    """Data for the journal account report."""

    charts: list[ChartData]
    journal: str


@dataclass(frozen=True)
class AccountReportTree:
    """Data for the tree account reports."""

    charts: list[ChartData]
    interval_balances: list[SerialisedTreeNode]
    budgets: dict[str, list[AccountBudget]]
    dates: list[DateRange]


@api_endpoint
def get_account_report() -> AccountReportJournal | AccountReportTree:
    """Get the data for the account report."""
    g.ledger.changed()

    account_name = request.args.get("a", "")
    subreport = request.args.get("r")

    charts = [
        ChartApi.account_balance(account_name),
        ChartApi.interval_totals(
            g.interval,
            account_name,
            label=gettext("Changes"),
        ),
    ]

    if subreport in {"changes", "balances"}:
        accumulate = subreport == "balances"
        interval_balances, dates = g.ledger.interval_balances(
            g.filtered,
            g.interval,
            account_name,
            accumulate=accumulate,
        )

        charts.append(ChartApi.hierarchy(account_name))
        charts.extend(
            ChartApi.hierarchy(
                account_name,
                date_range.begin,
                date_range.end,
                label=g.interval.format_date(date_range.begin),
            )
            for date_range in dates[:3]
        )

        all_accounts = (
            interval_balances[0].accounts if interval_balances else []
        )
        budget_accounts = [
            a for a in all_accounts if a.startswith(account_name)
        ]
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
                tree.get(account_name).serialise(
                    g.conversion,
                    g.ledger.prices,
                    date_range.end_inclusive,
                    with_cost=False,
                )
                for tree, date_range in zip(interval_balances, dates)
            ],
            dates=dates,
            budgets=budgets,
        )

    journal = get_template_attribute("_journal_table.html", "journal_table")
    entries = g.ledger.account_journal(
        g.filtered,
        account_name,
        g.conversion,
        with_children=g.ledger.fava_options.account_journal_include_children,
    )
    return AccountReportJournal(
        charts,
        journal=journal(entries, show_change_and_balance=True),
    )
