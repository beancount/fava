"""JSON API.

This module contains the url endpoints of the JSON API that is used by the web
interface for asynchronous functionality.
"""

import os
import functools

from flask import Blueprint, jsonify, g, request
from werkzeug.utils import secure_filename

from fava.serialisation import deserialise, serialise
from fava.core.file import save_entry_slice
from fava.core.helpers import FavaAPIException
from fava.core.misc import align

json_api = Blueprint("json_api", __name__)  # pylint: disable=invalid-name


def json_response(func):
    """Jsonify the response."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        json_data = func(*args, **kwargs)
        if "success" not in json_data:
            json_data["success"] = True
        return jsonify(json_data)

    return _wrapper


def json_request(func):
    """Check existence and load the JSON payload of the request."""

    @functools.wraps(func)
    def _wrapper():
        request_data = request.get_json()
        if request_data is None:
            raise FavaAPIException("Invalid JSON request.")
        return func(request_data)

    return _wrapper


@json_api.errorhandler(FavaAPIException)
@json_response
def _json_api_exception(error):
    return {"success": False, "error": error.message}


@json_api.errorhandler(OSError)
@json_response
def _json_api_oserror(error):
    return {"success": False, "error": error.strerror}


@json_api.route("/changed/")
@json_response
def changed():
    """Check for file changes."""
    return {"changed": g.ledger.changed()}


@json_api.route("/errors/")
@json_response
def errors():
    """Number of errors."""
    return {"errors": len(g.ledger.errors)}


@json_api.route("/source/", methods=["PUT"])
@json_request
@json_response
def source(request_data):
    """Write one of the source files."""
    if request_data.get("file_path"):
        sha256sum = g.ledger.file.set_source(
            request_data.get("file_path"),
            request_data.get("source"),
            request_data.get("sha256sum"),
        )
    else:
        entry = g.ledger.get_entry(request_data.get("entry_hash"))
        sha256sum = save_entry_slice(
            entry, request_data.get("source"), request_data.get("sha256sum")
        )
    return {"sha256sum": sha256sum}


@json_api.route("/format-source/", methods=["POST"])
@json_request
@json_response
def format_source(request_data):
    """Format beancount file."""
    aligned = align(request_data["source"], g.ledger.fava_options)
    return {"payload": aligned}


@json_api.route("/payee-accounts/", methods=["GET"])
@json_response
def payee_accounts():
    """Rank accounts for the given payee."""
    return {
        "payload": g.ledger.attributes.payee_accounts(
            request.args.get("payee")
        )
    }


@json_api.route("/payee-transaction/", methods=["GET"])
@json_response
def payee_transaction():
    """Last transaction for the given payee."""
    entry = g.ledger.attributes.payee_transaction(request.args.get("payee"))
    return {"payload": serialise(entry)}


@json_api.route("/add-document/", methods=["PUT"])
@json_response
def add_document():
    """Upload a document."""
    if not g.ledger.options["documents"]:
        raise FavaAPIException("You need to set a documents folder.")

    upload = request.files["file"]
    if not upload:
        raise FavaAPIException("No file uploaded.")

    documents_folder = request.form["folder"]
    if documents_folder not in g.ledger.options["documents"]:
        raise FavaAPIException(
            "Not a documents folder: {}.".format(documents_folder)
        )

    filename = upload.filename
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    if not os.path.supports_unicode_filenames:
        filename = secure_filename(filename)

    directory = os.path.normpath(
        os.path.join(
            os.path.dirname(g.ledger.beancount_file_path),
            documents_folder,
            *request.form["account"].split(":")
        )
    )
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        raise FavaAPIException("{} already exists.".format(filepath))

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    upload.save(filepath)

    if request.form.get("hash"):
        g.ledger.file.insert_metadata(
            request.form["hash"], "document", filename
        )
    return {"message": "Uploaded to {}".format(filepath)}


@json_api.route("/add-entries/", methods=["PUT"])
@json_request
@json_response
def add_entries(request_data):
    """Add multiple entries."""
    try:
        entries = [deserialise(entry) for entry in request_data["entries"]]
    except KeyError as error:
        raise FavaAPIException("KeyError: {}".format(str(error)))

    g.ledger.file.insert_entries(entries)

    return {"message": "Stored {} entries.".format(len(entries))}
