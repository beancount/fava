"""Fava's main WSGI application.

you can use `create_app` to create a Fava WSGI app for a given list of files.
To start a simple server::

    from fava.application import create_app

    app = create_app(['/path/to/file.beancount'])
    app.run('localhost', 5000)

"""

from __future__ import annotations

import logging
import mimetypes
from dataclasses import fields
from datetime import date
from datetime import datetime
from datetime import timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

import markdown2  # type: ignore[import-untyped]
from beancount import __version__ as beancount_version
from flask import abort
from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import render_template_string
from flask import request
from flask import send_file
from flask import url_for as flask_url_for
from flask_babel import Babel  # type: ignore[import-untyped]
from flask_babel import get_translations
from markupsafe import Markup
from werkzeug.utils import secure_filename

from fava import __version__ as fava_version
from fava import LOCALES
from fava import template_filters
from fava._ctx_globals_class import Context
from fava.beans import funcs
from fava.context import g
from fava.core import conversion
from fava.core import FavaLedger
from fava.core.charts import FavaJSONProvider
from fava.core.documents import is_document_or_import_file
from fava.help import HELP_PAGES
from fava.helpers import FavaAPIError
from fava.internal_api import ChartApi
from fava.internal_api import get_ledger_data
from fava.json_api import json_api
from fava.util import next_key
from fava.util import send_file_inline
from fava.util import setup_logging
from fava.util import slugify
from fava.util.excel import HAVE_EXCEL

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterable

    from flask.wrappers import Response
    from werkzeug import Response as WerkzeugResponse


setup_logging()

SERVER_SIDE_REPORTS = [
    "journal",
    "options",
    "statistics",
]

CLIENT_SIDE_REPORTS = [
    "balance_sheet",
    "commodities",
    "documents",
    "editor",
    "errors",
    "events",
    "holdings",
    "import",
    "income_statement",
    "query",
    "trial_balance",
]


if not mimetypes.types_map.get(".js", "").endswith("/javascript"):
    # This is sometimes broken on windows, see
    # https://github.com/beancount/fava/issues/1446
    logging.error("Invalid mimetype set for '.js', overriding")
    mimetypes.add_type("text/javascript", ".js")


def _ledger_slugs_dict(ledgers: Iterable[FavaLedger]) -> dict[str, FavaLedger]:
    """Get dictionary mapping URL slugs to ledgers."""
    ledgers_by_slug: dict[str, FavaLedger] = {}
    for ledger in ledgers:
        title_slug = slugify(ledger.options["title"])
        slug = title_slug or slugify(ledger.beancount_file_path)
        unique_key = next_key(slug, ledgers_by_slug)
        ledgers_by_slug[unique_key] = ledger
    return ledgers_by_slug


def static_url(filename: str) -> str:
    """Return a static url with an mtime query string for cache busting."""
    file_path = Path(__file__).parent / "static" / filename
    try:
        mtime = str(int(file_path.stat().st_mtime))
    except FileNotFoundError:
        mtime = "0"
    return url_for("static", filename=filename, mtime=mtime)


_cached_url_for = lru_cache(2048)(flask_url_for)


def _inject_filters(endpoint: str, values: dict[str, str]) -> None:
    if (
        "bfile" not in values
        and current_app.url_map.is_endpoint_expecting(endpoint, "bfile")
        and g.beancount_file_slug is not None
    ):
        values["bfile"] = g.beancount_file_slug
    if endpoint in {"static", "index"}:
        return
    for name in ("conversion", "interval", "account", "filter", "time"):
        if name not in values:
            val = request.args.get(name)
            if val is not None:
                values[name] = val


def url_for(endpoint: str, **values: str) -> str:
    """Wrap flask.url_for using a cache."""
    _inject_filters(endpoint, values)
    return _cached_url_for(endpoint, **values)


def translations() -> dict[str, str]:
    """Get translations catalog."""
    return get_translations()._catalog  # type: ignore[no-any-return]  # noqa: SLF001


def _setup_template_config(fava_app: Flask, *, incognito: bool) -> None:
    """Setup jinja, template filters and globals."""
    # Jinja config
    fava_app.jinja_options = {
        "extensions": ["jinja2.ext.do", "jinja2.ext.loopcontrols"],
        "trim_blocks": True,
        "lstrip_blocks": True,
    }

    # Add template filters
    fava_app.add_template_filter(conversion.units)
    fava_app.add_template_filter(funcs.hash_entry)
    fava_app.add_template_filter(template_filters.basename)
    fava_app.add_template_filter(template_filters.flag_to_type)
    fava_app.add_template_filter(template_filters.format_currency)
    fava_app.add_template_filter(template_filters.meta_items)
    fava_app.add_template_filter(fields, "dataclass_fields")
    fava_app.add_template_filter(
        template_filters.replace_numbers
        if incognito
        else template_filters.passthrough_numbers,
        "incognito",
    )

    # Add template global functions
    fava_app.add_template_global(static_url, "static_url")
    fava_app.add_template_global(date.today, "today")
    fava_app.add_template_global(url_for, "url_for")
    fava_app.add_template_global(translations, "translations")
    fava_app.add_template_global(get_ledger_data, "get_ledger_data")

    @fava_app.context_processor
    def _template_context() -> dict[str, FavaLedger | type[ChartApi]]:
        """Inject variables into the template context."""
        return {"ledger": g.ledger, "chart_api": ChartApi}


def _setup_filters(
    fava_app: Flask,
    *,
    read_only: bool,
) -> None:
    """Setup request handlers/filters."""
    fava_app.url_defaults(_inject_filters)

    @fava_app.before_request
    def _perform_global_filters() -> None:
        if request.endpoint in {"json_api.get_changed", "json_api.get_errors"}:
            return
        ledger = getattr(g, "ledger", None)
        if ledger:
            # check (and possibly reload) source file
            if request.blueprint != "json_api":
                ledger.changed()

            ledger.extensions.before_request()

    if read_only:
        # Prevent any request that isn't a GET if read-only mode is active
        @fava_app.before_request
        def _read_only() -> None:
            if request.method != "GET":
                abort(401)

    load_file_lock = Lock()

    @fava_app.url_value_preprocessor
    def _pull_beancount_file(
        _: str | None,
        values: dict[str, str] | None,
    ) -> None:
        g.beancount_file_slug = values.pop("bfile", None) if values else None
        if not fava_app.config["LEDGERS"]:
            with load_file_lock:
                if not fava_app.config["LEDGERS"]:
                    fava_app.config["LEDGERS"] = _ledger_slugs_dict(
                        FavaLedger(
                            filepath,
                            poll_watcher=fava_app.config["POLL_WATCHER"],
                        )
                        for filepath in fava_app.config["BEANCOUNT_FILES"]
                    )
        if g.beancount_file_slug:
            if g.beancount_file_slug not in fava_app.config["LEDGERS"]:
                # one of the file slugs might have changed, update the mapping
                fava_app.config["LEDGERS"] = _ledger_slugs_dict(
                    fava_app.config["LEDGERS"].values(),
                )
                if g.beancount_file_slug not in fava_app.config["LEDGERS"]:
                    abort(404)
            g.ledger = fava_app.config["LEDGERS"][g.beancount_file_slug]

    @fava_app.errorhandler(FavaAPIError)
    def fava_api_exception(error: FavaAPIError) -> str:
        """Handle API errors."""
        return render_template(
            "_layout.html",
            page_title="Error",
            content=error.message,
        )


def _setup_routes(fava_app: Flask) -> None:  # noqa: PLR0915
    @fava_app.route("/")
    @fava_app.route("/<bfile>/")
    def index() -> WerkzeugResponse:
        """Redirect to the Income Statement (of the given or first file)."""
        if not g.beancount_file_slug:
            g.beancount_file_slug = next(iter(fava_app.config["LEDGERS"]))
        index_url = url_for("index")
        default_page = fava_app.config["LEDGERS"][
            g.beancount_file_slug
        ].fava_options.default_page
        return redirect(f"{index_url}{default_page}")

    @fava_app.route("/<bfile>/account/<name>/")
    def account(name: str) -> str:
        """Get the account report."""
        return render_template("_layout.html", content="", name=name)

    @fava_app.route("/<bfile>/document/", methods=["GET"])
    def document() -> Response:
        """Download a document."""
        filename = request.args.get("filename", "")
        if is_document_or_import_file(filename, g.ledger):
            return send_file_inline(filename)
        return abort(404)

    @fava_app.route("/<bfile>/statement/", methods=["GET"])
    def statement() -> Response:
        """Download a statement file."""
        entry_hash = request.args.get("entry_hash", "")
        key = request.args.get("key", "")
        document_path = g.ledger.statement_path(entry_hash, key)
        return send_file_inline(document_path)

    @fava_app.route(
        "/<bfile>/holdings"
        "/by_<any(account,currency,cost_currency):aggregation_key>/",
    )
    def holdings_by(
        **_kwargs: str,
    ) -> str:
        """Get the client-side-rendered holdings report."""
        return render_template("_layout.html", content="")

    @fava_app.route("/<bfile>/<report_name>/")
    def report(report_name: str) -> str:
        """Endpoint for most reports."""
        if report_name in CLIENT_SIDE_REPORTS:
            return render_template("_layout.html", content="")
        if report_name in SERVER_SIDE_REPORTS:
            return render_template(f"{report_name}.html")
        return abort(404)

    @fava_app.route(
        "/<bfile>/extension/<extension_name>/<endpoint>",
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    def extension_endpoint(extension_name: str, endpoint: str) -> Response:
        ext = g.ledger.extensions.get_extension(extension_name)
        key = (endpoint, request.method)
        if ext is None or key not in ext.endpoints:
            return abort(404)
        response = ext.endpoints[key](ext)

        return (
            fava_app.make_response(response)
            if response is not None
            else abort(404)
        )

    @fava_app.route("/<bfile>/extension_js_module/<extension_name>.js")
    def extension_js_module(extension_name: str) -> Response:
        """Endpoint for extension module source."""
        ext = g.ledger.extensions.get_extension(extension_name)
        if ext is None or not ext.has_js_module:
            return abort(404)
        return send_file(ext.extension_dir / f"{ext.name}.js")

    @fava_app.route("/<bfile>/extension/<extension_name>/")
    def extension_report(extension_name: str) -> str:
        """Endpoint for extension reports."""
        ext = g.ledger.extensions.get_extension(extension_name)
        if ext is None or ext.report_title is None:
            abort(404)

        g.extension = ext
        template = ext.jinja_env.get_template(f"{ext.name}.html")
        content = Markup(template.render(ledger=g.ledger, extension=ext))
        return render_template(
            "_layout.html",
            content=content,
            page_title=ext.report_title,
        )

    @fava_app.route("/<bfile>/download-query/query_result.<result_format>")
    def download_query(result_format: str) -> Response:
        """Download a query result."""
        name, data = g.ledger.query_shell.query_to_file(
            g.filtered.entries,
            request.args.get("query_string", ""),
            result_format,
        )

        filename = f"{secure_filename(name.strip())}.{result_format}"
        return send_file(data, as_attachment=True, download_name=filename)

    @fava_app.route("/<bfile>/download-journal/")
    def download_journal() -> Response:
        """Download a Journal file."""
        now = datetime.now(tz=timezone.utc).replace(microsecond=0)
        filename = f"journal_{now.isoformat()}.beancount"
        data = BytesIO(bytes(render_template("beancount_file"), "utf8"))
        return send_file(data, as_attachment=True, download_name=filename)

    @fava_app.route("/<bfile>/help/", defaults={"page_slug": "_index"})
    @fava_app.route("/<bfile>/help/<page_slug>")
    def help_page(page_slug: str) -> str:
        """Fava's included documentation."""
        if page_slug not in HELP_PAGES:
            abort(404)
        html = markdown2.markdown_path(
            (Path(__file__).parent / "help" / (page_slug + ".md")),
            extras=["fenced-code-blocks", "tables", "header-ids"],
        )
        return render_template(
            "help.html",
            page_slug=page_slug,
            help_html=Markup(
                render_template_string(
                    html,
                    beancount_version=beancount_version,
                    fava_version=fava_version,
                ),
            ),
            HELP_PAGES=HELP_PAGES,
        )

    @fava_app.route("/jump")
    def jump() -> WerkzeugResponse:
        """Redirect back to the referer, replacing some parameters.

        This is useful for sidebar links, e.g. a link ``/jump?time=year``
        would set the time filter to `year` on the current page.

        When accessing ``/jump?param1=abc`` from
        ``/example/page?param1=123&param2=456``, this view should redirect to
        ``/example/page?param1=abc&param2=456``.

        """
        url = urlparse(request.referrer)
        query_args = parse_qsl(url.query)
        for key, values in request.args.lists():
            query_args = [
                key_value for key_value in query_args if key_value[0] != key
            ]
            if values != [""]:
                query_args.extend([(key, v) for v in values])

        redirect_url = url._replace(query=urlencode(query_args))
        return redirect(urlunparse(redirect_url))


def _setup_babel(fava_app: Flask) -> None:
    """Configure the Babel Flask extension."""

    def _get_locale() -> str | None:
        """Get locale."""
        lang = g.ledger.fava_options.language
        if lang is not None:
            return lang
        return request.accept_languages.best_match(["en", *LOCALES])

    try:
        # for Flask-Babel <3.0
        babel = Babel(fava_app)
        babel.localeselector(_get_locale)
    except AttributeError:
        # for Flask-Babel >=3.0
        babel = Babel(fava_app, locale_selector=_get_locale)


def create_app(
    files: Iterable[Path | str],
    *,
    load: bool = False,
    incognito: bool = False,
    read_only: bool = False,
    poll_watcher: bool = False,
) -> Flask:
    """Create a Fava Flask application.

    Arguments:
        files: The list of Beancount files (paths).
        load: Whether to load the Beancount files directly.
        incognito: Whether to run in incognito mode.
        read_only: Whether to run in read-only mode.
        poll_watcher: Whether to use old poll watcher
    """
    fava_app = Flask("fava")
    fava_app.register_blueprint(json_api, url_prefix="/<bfile>/api")
    fava_app.json = FavaJSONProvider(fava_app)
    fava_app.app_ctx_globals_class = Context  # type: ignore[assignment]
    _setup_template_config(fava_app, incognito=incognito)
    _setup_babel(fava_app)
    _setup_filters(fava_app, read_only=read_only)
    _setup_routes(fava_app)

    fava_app.config["HAVE_EXCEL"] = HAVE_EXCEL
    fava_app.config["BEANCOUNT_FILES"] = [str(f) for f in files]
    fava_app.config["INCOGNITO"] = incognito
    fava_app.config["POLL_WATCHER"] = poll_watcher

    if load:
        fava_app.config["LEDGERS"] = _ledger_slugs_dict(
            FavaLedger(filepath, poll_watcher=poll_watcher)
            for filepath in fava_app.config["BEANCOUNT_FILES"]
        )
    else:
        fava_app.config["LEDGERS"] = None

    return fava_app


#: This is still provided for compatibility but will be removed at some point.
app = create_app([])
