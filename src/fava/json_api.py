"""JSON API.

This module contains the url endpoints of the JSON API that is used by the web
interface for asynchronous functionality.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from functools import wraps
from inspect import Parameter
from inspect import signature
from os import path
from os import remove
from typing import Any
from typing import Callable
from typing import Mapping
from typing import TYPE_CHECKING

from flask import Blueprint
from flask import get_template_attribute
from flask import jsonify
from flask import request

from fava.beans.abc import Document
from fava.beans.abc import Event
from fava.context import g
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.core.ingest import filepath_in_primary_imports_folder
from fava.core.misc import align
from fava.helpers import FavaAPIError
from fava.internal_api import get_errors
from fava.internal_api import get_ledger_data
from fava.serialisation import deserialise
from fava.serialisation import serialise

if TYPE_CHECKING:  # pragma: no cover
    from datetime import date
    from decimal import Decimal

    from flask.wrappers import Response

    from fava.core.ingest import FileImporters


json_api = Blueprint("json_api", __name__)


class ValidationError(Exception):
    """Validation of data failed."""


def json_err(msg: str) -> Response:
    """Jsonify the error message."""
    return jsonify({"success": False, "error": msg})


def json_success(data: Any) -> Response:
    """Jsonify the response."""
    return jsonify(
        {"success": True, "data": data, "mtime": str(g.ledger.mtime)}
    )


@json_api.errorhandler(FavaAPIError)
def _json_api_exception(error: FavaAPIError) -> Response:
    return json_err(error.message)


@json_api.errorhandler(OSError)
def _json_api_oserror(error: OSError) -> Response:
    return json_err(error.strerror)


@json_api.errorhandler(ValidationError)
def _json_api_validation_error(error: ValidationError) -> Response:
    return json_err(f"Invalid API request: {str(error)}")


def validate_func_arguments(
    func: Callable[..., Any]
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
        assert param.annotation in {
            "str",
            "list[Any]",
        }, f"Type of param {param.name} needs to str or list"
        assert (
            param.kind == Parameter.POSITIONAL_OR_KEYWORD
        ), f"Param {param.name} should be positional"
        params.append((param.name, str if param.annotation == "str" else list))

    if not params:
        return None

    def validator(mapping: Mapping[str, str]) -> list[str]:
        args: list[str] = []
        for param, type_ in params:
            val = mapping.get(param, None)
            if val is None:
                raise ValidationError(f"Parameter `{param}` is missing.")
            if not isinstance(val, type_):
                raise ValidationError(
                    f"Parameter `{param}` of incorrect type."
                )
            args.append(val)
        return args

    return validator


def api_endpoint(func: Callable[..., Any]) -> Callable[[], Response]:
    """
    Register an API endpoint.

    The part of the function name up to the first underscore determines
    the accepted HTTP method. For GET and DELETE endpoints, the function
    parameters are extracted from the URL query string and passed to the
    decorated endpoint handler.
    """
    method, _, name = func.__name__.partition("_")
    assert method in {"get", "delete", "put"}, func.__name__
    validator = validate_func_arguments(func)

    @json_api.route(f"/{name}", methods=[method])
    @wraps(func)
    def _wrapper() -> Response:
        if validator is not None:
            if method == "put":
                request_json = request.get_json(silent=True)
                if request_json is None:
                    raise FavaAPIError("Invalid JSON request.")
                data = request_json
            else:
                data = request.args
            res = func(*validator(data))
        else:
            res = func()
        return json_success(res)

    return _wrapper


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


@dataclass
class QueryResult:
    """Table and optional chart returned by the query_result endpoint."""

    table: Any
    chart: Any | None = None


@api_endpoint
def get_query_result(query_string: str) -> Any:
    """Render a query result to HTML."""
    table = get_template_attribute("_query_table.html", "querytable")
    contents, types, rows = g.ledger.query_shell.execute_query(
        g.filtered.entries, query_string
    )
    if contents and "ERROR" in contents:
        raise FavaAPIError(contents)
    table = table(g.ledger, contents, types, rows)

    if types and g.ledger.charts.can_plot_query(types):
        return QueryResult(table, g.ledger.charts.query(types, rows))
    return QueryResult(table)


@api_endpoint
def get_extract(filename: str, importer: str) -> list[Any]:
    """Extract entries using the ingest framework."""
    entries = g.ledger.ingest.extract(filename, importer)
    return list(map(serialise, entries))


@dataclass
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
        raise FavaAPIError("You need to set a documents folder.")

    new_path = filepath_in_document_folder(
        g.ledger.options["documents"][0], account, new_name, g.ledger
    )

    if not path.isfile(filename):
        raise FavaAPIError(f"Not a file: '{filename}'")
    if path.exists(new_path):
        raise FavaAPIError(f"Target file exists: '{new_path}'")

    if not path.exists(path.dirname(new_path)):
        os.makedirs(path.dirname(new_path), exist_ok=True)
    shutil.move(filename, new_path)

    return f"Moved {filename} to {new_path}."


@api_endpoint
def get_payee_transaction(payee: str) -> Any:
    """Last transaction for the given payee."""
    entry = g.ledger.attributes.payee_transaction(payee)
    return serialise(entry) if entry else None


@api_endpoint
def get_source(filename: str) -> Any:
    """Load one of the source files."""
    file_path = (
        filename
        or g.ledger.fava_options.default_file
        or g.ledger.beancount_file_path
    )
    source, sha256sum = g.ledger.file.get_source(file_path)
    return {"source": source, "sha256sum": sha256sum, "file_path": file_path}


@api_endpoint
def put_source(file_path: str, source: str, sha256sum: str) -> str:
    """Write one of the source files and return the updated sha256sum."""
    return g.ledger.file.set_source(file_path, source, sha256sum)


@api_endpoint
def put_source_slice(entry_hash: str, source: str, sha256sum: str) -> str:
    """Write an entry source slice and return the updated sha256sum."""
    return g.ledger.file.save_entry_slice(entry_hash, source, sha256sum)


@api_endpoint
def put_format_source(source: str) -> str:
    """Format beancount file."""
    return align(source, g.ledger.fava_options.currency_column)


@api_endpoint
def delete_document(filename: str) -> str:
    """Delete a document."""
    if not is_document_or_import_file(filename, g.ledger):
        raise FavaAPIError("No valid document or import file.")

    if not path.exists(filename):
        raise FavaAPIError(f"{filename} does not exist.")

    remove(filename)
    return f"Deleted {filename}."


@api_endpoint
def put_add_document() -> str:
    """Upload a document."""
    if not g.ledger.options["documents"]:
        raise FavaAPIError("You need to set a documents folder.")

    upload = request.files.get("file", None)

    if not upload:
        raise FavaAPIError("No file uploaded.")
    if not upload.filename:
        raise FavaAPIError("Uploaded file is missing filename.")

    filepath = filepath_in_document_folder(
        request.form["folder"],
        request.form["account"],
        upload.filename,
        g.ledger,
    )
    directory, filename = path.split(filepath)

    if path.exists(filepath):
        raise FavaAPIError(f"{filepath} already exists.")

    if not path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    upload.save(filepath)

    if request.form.get("hash"):
        g.ledger.file.insert_metadata(
            request.form["hash"], "document", filename
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
        raise FavaAPIError(f"KeyError: {error}") from error

    g.ledger.file.insert_entries(entries)

    return f"Stored {len(entries)} entries."


@api_endpoint
def put_upload_import_file() -> str:
    """Upload a file for importing."""
    upload = request.files.get("file", None)

    if not upload:
        raise FavaAPIError("No file uploaded.")
    if not upload.filename:
        raise FavaAPIError("Uploaded file is missing filename.")
    filepath = filepath_in_primary_imports_folder(upload.filename, g.ledger)

    directory = path.dirname(filepath)

    if path.exists(filepath):
        raise FavaAPIError(f"{filepath} already exists.")

    if not path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    upload.save(filepath)

    return f"Uploaded to {filepath}"


########################################################################
# Reports


@api_endpoint
def get_events() -> list[Event]:
    """Get all (filtered) events."""
    g.ledger.changed()
    return [e for e in g.filtered.entries if isinstance(e, Event)]


@api_endpoint
def get_imports() -> list[FileImporters]:
    """Get a list of the importable files."""
    g.ledger.changed()
    return g.ledger.ingest.import_data()


@api_endpoint
def get_documents() -> list[Document]:
    """Get all (filtered) documents."""
    g.ledger.changed()
    return [e for e in g.filtered.entries if isinstance(e, Document)]


@dataclass
class CommodityPairWithPrices:
    """A pair of commodities and prices for them."""

    base: str
    quote: str
    prices: list[tuple[date, Decimal]]


@api_endpoint
def get_commodities() -> list[CommodityPairWithPrices]:
    """Get the prices for all commodity pairs.

    Returns:
        A list of CommodityPairWithPrices
    """
    g.ledger.changed()
    ret = []
    for base, quote in g.ledger.commodity_pairs():
        prices = g.filtered.prices(base, quote)
        if prices:
            ret.append(CommodityPairWithPrices(base, quote, prices))

    return ret
