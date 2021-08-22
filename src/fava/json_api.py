"""JSON API.

This module contains the url endpoints of the JSON API that is used by the web
interface for asynchronous functionality.
"""
import functools
import os
import shutil
from os import path
from os import remove
from typing import List

from flask import Blueprint
from flask import get_template_attribute
from flask import jsonify
from flask import render_template
from flask import request

from fava.context import g
from fava.core.documents import filepath_in_document_folder
from fava.core.documents import is_document_or_import_file
from fava.core.misc import align
from fava.helpers import FavaAPIException
from fava.serialisation import deserialise
from fava.serialisation import serialise

json_api = Blueprint("json_api", __name__)  # pylint: disable=invalid-name


def get_api_endpoint(func):
    """Register a GET endpoint."""

    @json_api.route(f"/{func.__name__}", methods=["GET"])
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return jsonify({"success": True, "data": func(*args, **kwargs)})

    return _wrapper


def put_api_endpoint(func):
    """Register a PUT endpoint."""

    @json_api.route(f"/{func.__name__}", methods=["PUT"])
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        request_data = request.get_json()
        if request_data is None:
            raise FavaAPIException("Invalid JSON request.")
        res = func(request_data, *args, **kwargs)
        return jsonify({"success": True, "data": res})

    return _wrapper


def delete_api_endpoint(func):
    """Register a DELETE endpoint."""

    route = func.__name__.replace("delete_", "")

    @json_api.route(f"/{route}", methods=["DELETE"])
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return jsonify({"success": True, "data": func(*args, **kwargs)})

    return _wrapper


def json_response(func):
    """Jsonify the response."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        json_data = func(*args, **kwargs)
        if "success" not in json_data:
            json_data["success"] = True
        return jsonify(json_data)

    return _wrapper


@json_api.errorhandler(FavaAPIException)
@json_response
def _json_api_exception(error):
    return {"success": False, "error": error.message}


@json_api.errorhandler(OSError)
@json_response
def _json_api_oserror(error):
    return {"success": False, "error": error.strerror}


@get_api_endpoint
def changed() -> bool:
    """Check for file changes."""
    return g.ledger.changed()


@get_api_endpoint
def errors() -> int:
    """Number of errors."""
    return len(g.ledger.errors)


@get_api_endpoint
def payee_accounts() -> List[str]:
    """Rank accounts for the given payee."""
    payee = request.args.get("payee", "")
    return g.ledger.attributes.payee_accounts(payee)


@get_api_endpoint
def query_result():
    """Render a query result to HTML."""
    query = request.args.get("query_string", "")
    table = get_template_attribute("_query_table.html", "querytable")
    contents, types, rows = g.ledger.query_shell.execute_query(query)
    if contents:
        if "ERROR" in contents:
            raise FavaAPIException(contents)
    table = table(g.ledger, contents, types, rows)

    if types and g.ledger.charts.can_plot_query(types):
        return {
            "chart": g.ledger.charts.query(types, rows),
            "table": table,
        }
    return {"table": table}


@get_api_endpoint
def extract():
    """Extract entries using the ingest framework."""
    entries = g.ledger.ingest.extract(
        request.args.get("filename"), request.args.get("importer")
    )
    return list(map(serialise, entries))


@get_api_endpoint
def context():
    """Entry context."""
    entry_hash = request.args.get("entry_hash")
    entry, balances, slice_, sha256sum = g.ledger.context(entry_hash)
    content = render_template("_context.html", entry=entry, balances=balances)
    return {"content": content, "sha256sum": sha256sum, "slice": slice_}


@get_api_endpoint
def move() -> str:
    """Move a file."""
    if not g.ledger.options["documents"]:
        raise FavaAPIException("You need to set a documents folder.")

    account = request.args.get("account")
    new_name = request.args.get("newName")
    filename = request.args.get("filename")

    if not account:
        raise FavaAPIException("No account specified.")

    if not filename:
        raise FavaAPIException("No filename specified.")

    if not new_name:
        raise FavaAPIException("No new filename given.")

    new_path = filepath_in_document_folder(
        g.ledger.options["documents"][0], account, new_name, g.ledger
    )

    if not path.isfile(filename):
        raise FavaAPIException(f"Not a file: '{filename}'")

    if path.exists(new_path):
        raise FavaAPIException(f"Target file exists: '{new_path}'")

    if not path.exists(path.dirname(new_path)):
        os.makedirs(path.dirname(new_path), exist_ok=True)

    shutil.move(filename, new_path)

    return f"Moved {filename} to {new_path}."


@get_api_endpoint
def payee_transaction():
    """Last transaction for the given payee."""
    entry = g.ledger.attributes.payee_transaction(request.args.get("payee"))
    return serialise(entry)


@put_api_endpoint
def source(request_data) -> str:
    """Write one of the source files and return the updated sha256sum."""
    return g.ledger.file.set_source(
        request_data.get("file_path"),
        request_data.get("source"),
        request_data.get("sha256sum"),
    )


@put_api_endpoint
def source_slice(request_data) -> str:
    """Write an entry source slice and return the updated sha256sum."""
    return g.ledger.file.save_entry_slice(
        request_data.get("entry_hash"),
        request_data.get("source"),
        request_data.get("sha256sum"),
    )


@put_api_endpoint
def format_source(request_data) -> str:
    """Format beancount file."""
    return align(
        request_data["source"], g.ledger.fava_options["currency-column"]
    )


@delete_api_endpoint
def delete_document() -> str:
    """Delete a document."""
    filename = request.args.get("filename")
    if not filename:
        raise FavaAPIException("No filename specified.")

    if not is_document_or_import_file(filename, g.ledger):
        raise FavaAPIException("No valid document or import file.")

    if not path.exists(filename):
        raise FavaAPIException(f"{filename} does not exist.")

    remove(filename)
    return f"Deleted {filename}."


@json_api.route("/add_document", methods=["PUT"])
@json_response
def add_document():
    """Upload a document."""
    if not g.ledger.options["documents"]:
        raise FavaAPIException("You need to set a documents folder.")

    upload = request.files["file"]

    if not upload:
        raise FavaAPIException("No file uploaded.")

    filepath = filepath_in_document_folder(
        request.form["folder"],
        request.form["account"],
        upload.filename,
        g.ledger,
    )
    directory, filename = path.split(filepath)

    if path.exists(filepath):
        raise FavaAPIException(f"{filepath} already exists.")

    if not path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    upload.save(filepath)

    if request.form.get("hash"):
        g.ledger.file.insert_metadata(
            request.form["hash"], "document", filename
        )
    return {"data": f"Uploaded to {filepath}"}


@put_api_endpoint
def attach_document(request_data):
    """Attach a document to an entry."""
    filename = request_data["filename"]
    entry_hash = request_data["entry_hash"]
    g.ledger.file.insert_metadata(entry_hash, "document", filename)
    return f"Attached '{filename}' to entry."


@put_api_endpoint
def add_entries(request_data):
    """Add multiple entries."""
    try:
        entries = [deserialise(entry) for entry in request_data["entries"]]
    except KeyError as error:
        raise FavaAPIException(f"KeyError: {error}") from error

    g.ledger.file.insert_entries(entries)

    return f"Stored {len(entries)} entries."
