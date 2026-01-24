"""rustfava's main WSGI application.

you can use `create_app` to create a rustfava WSGI app for a given list of files.
To start a simple server::

    from rustfava.application import create_app

    app = create_app(['/path/to/file.beancount'])
    app.run('localhost', 5000)

"""

from __future__ import annotations

import gzip
import logging
import mimetypes
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

from flask import abort
from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import render_template_string
from flask import request
from flask import send_file
from flask import url_for as flask_url_for
from flask_babel import Babel
from flask_babel import get_translations
from markupsafe import Markup
from werkzeug.utils import secure_filename

from rustfava import LOCALES
from rustfava import template_filters
from rustfava._ctx_globals_class import Context
from rustfava.beans import funcs
from rustfava.context import g
from rustfava.core import RustfavaLedger
from rustfava.core.charts import RustfavaJSONProvider
from rustfava.core.documents import is_document_or_import_file
from rustfava.help import HELP_PAGES
from rustfava.helpers import RustfavaAPIError
from rustfava.internal_api import ChartApi
from rustfava.internal_api import get_ledger_data
from rustfava.json_api import json_api
from rustfava.util import next_key
from rustfava.util import send_file_inline
from rustfava.util import setup_logging
from rustfava.util import slugify
from rustfava.util.excel import HAVE_EXCEL

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView
    from collections.abc import Iterable

    from flask.wrappers import Response
    from werkzeug import Response as WerkzeugResponse


setup_logging()

CLIENT_SIDE_REPORTS = [
    "balance_sheet",
    "commodities",
    "documents",
    "editor",
    "errors",
    "events",
    "holdings",
    "import",
    "journal",
    "income_statement",
    "options",
    "query",
    "statistics",
    "trial_balance",
]

log = logging.getLogger(__name__)


if not mimetypes.types_map.get(".js", "").endswith(
    "/javascript"
):  # pragma: no cover
    # This is sometimes broken on windows, see
    # https://github.com/beancount/fava/issues/1446
    log.error("Invalid mimetype set for '.js', overriding")
    mimetypes.add_type("text/javascript", ".js")


def _slug(ledger: RustfavaLedger) -> str:
    """Slug for a ledger."""
    title_slug = slugify(ledger.options["title"])
    return title_slug or slugify(ledger.beancount_file_path)


class _LedgerSlugLoader:
    """Load multiple ledgers and access them by their slug."""

    def __init__(
        self,
        fava_app: Flask,
        *,
        load: bool = False,
        poll_watcher: bool = False,
    ) -> None:
        self.fava_app = fava_app
        self.poll_watcher = poll_watcher

        self._lock = Lock()

        # The loaded ledgers - lazily loaded unless load=True
        self._ledgers = None
        # The titles of the ledgers - used to check whether the ledgers_by_slug
        # below needs to be re-computed
        self._titles: list[str] | None = None
        # Cache the dict of ledgers by their slugs
        self._ledgers_by_slug: dict[str, RustfavaLedger] | None = None

        if load:
            with self._lock:
                self._ledgers = self._load()

    def _load(self) -> list[RustfavaLedger]:
        return [
            RustfavaLedger(path, poll_watcher=self.poll_watcher)
            for path in self.fava_app.config["BEANCOUNT_FILES"]
        ]

    @property
    def ledgers(self) -> list[RustfavaLedger]:
        """Return the list of loaded ledgers (loading it if not yet done)."""
        if self._ledgers is None:
            with self._lock:
                # avoid loading it already loaded while waiting for the lock
                if self._ledgers is None:  # pragma: no cover
                    self._ledgers = self._load()
        return self._ledgers  # ty:ignore[invalid-return-type]

    @property
    def ledgers_by_slug(self) -> dict[str, RustfavaLedger]:
        """A dict mapping slugs to the loaded ledgers."""
        ledgers = self.ledgers
        titles = [ledger.options["title"] for ledger in ledgers]
        if self._ledgers_by_slug is None or self._titles != titles:
            by_slug: dict[str, RustfavaLedger] = {}
            for ledger in ledgers:
                by_slug[next_key(_slug(ledger), by_slug)] = ledger
            self._ledgers_by_slug = by_slug
            self._titles = titles
        return self._ledgers_by_slug

    def first_slug(self) -> str:
        """Get the slug of the first ledger."""
        return _slug(self.ledgers[0])

    def items(self) -> ItemsView[str, RustfavaLedger]:
        """Get an items view of all the ledgers by slug."""
        return self.ledgers_by_slug.items()

    def __getitem__(self, slug: str) -> RustfavaLedger:
        """Get the ledger for the given slug."""
        return self.ledgers_by_slug[slug]


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
    catalog = get_translations()._catalog  # noqa: SLF001
    return {k: v for k, v in catalog.items() if isinstance(k, str) and k}


def _setup_template_config(fava_app: Flask, *, incognito: bool) -> None:
    """Setup jinja, template filters and globals."""
    # Jinja config
    fava_app.jinja_options = {
        "extensions": ["jinja2.ext.do", "jinja2.ext.loopcontrols"],
        "trim_blocks": True,
        "lstrip_blocks": True,
    }

    # Add template filters
    fava_app.add_template_filter(funcs.hash_entry)
    fava_app.add_template_filter(template_filters.basename)
    fava_app.add_template_filter(template_filters.flag_to_type)
    fava_app.add_template_filter(template_filters.format_currency)
    fava_app.add_template_filter(template_filters.meta_items)
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
    def _template_context() -> dict[str, RustfavaLedger | type[ChartApi]]:
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

    @fava_app.url_value_preprocessor
    def _pull_beancount_file(
        _: str | None,
        values: dict[str, str] | None,
    ) -> None:
        g.beancount_file_slug = values.pop("bfile", None) if values else None
        if g.beancount_file_slug:
            try:
                ledgers: _LedgerSlugLoader = fava_app.config["LEDGERS"]
                g.ledger = ledgers[g.beancount_file_slug]
            except KeyError:
                abort(404)

    @fava_app.errorhandler(RustfavaAPIError)
    def fava_api_exception(error: RustfavaAPIError) -> tuple[str, int]:
        """Handle API errors."""
        return render_template(
            "_layout.html", page_title="Error", content=error.message
        ), 500

    @fava_app.after_request
    def _compress_response(response: Response) -> Response:
        """Compress JSON responses with gzip if client supports it."""
        # Only compress JSON responses over 500 bytes
        if (
            response.content_type
            and "application/json" in response.content_type
            and response.content_length
            and response.content_length > 500
            and any(enc == "gzip" for enc, _ in request.accept_encodings)
        ):
            response.data = gzip.compress(response.data)
            response.headers["Content-Encoding"] = "gzip"
            response.headers["Content-Length"] = len(response.data)
        return response


def _setup_routes(fava_app: Flask) -> None:  # noqa: PLR0915
    @fava_app.route("/")
    @fava_app.route("/<bfile>/")
    def index() -> WerkzeugResponse:
        """Redirect to the Income Statement (of the given or first file)."""
        ledgers: _LedgerSlugLoader = fava_app.config["LEDGERS"]
        if not g.beancount_file_slug:
            g.beancount_file_slug = ledgers.first_slug()
        index_url = url_for("index")
        default_page = ledgers[g.beancount_file_slug].fava_options.default_page
        return redirect(f"{index_url}{default_page}")

    @fava_app.route("/<bfile>/account/<name>/")
    def account(name: str) -> str:  # noqa: ARG001
        """Get the account report."""
        return render_template("_layout.html", content="")

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
    def holdings_by(**_kwargs: str) -> str:
        """Get the client-side-rendered holdings report."""
        return render_template("_layout.html", content="")

    @fava_app.route("/<bfile>/<report_name>/")
    def report(report_name: str) -> str:
        """Endpoint for most reports."""
        if report_name in CLIENT_SIDE_REPORTS:
            return render_template("_layout.html", content="")
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
            return abort(404)

        g.extension = ext
        template = ext.jinja_env.get_template(f"{ext.name}.html")
        content = Markup(template.render(ledger=g.ledger, extension=ext))  # noqa: S704
        return render_template(
            "_layout.html",
            content=content,
            page_title=ext.report_title,
        )

    @fava_app.route("/<bfile>/download-query/query_result.<result_format>")
    def download_query(result_format: str) -> Response:
        """Download a query result."""
        name, data = g.ledger.query_shell.query_to_file(
            g.filtered.entries_with_all_prices,
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
        """rustfava's included documentation."""
        from importlib.metadata import version

        from markdown2 import markdown

        # Validate against whitelist (defense-in-depth: also check for path traversal)
        if page_slug not in HELP_PAGES or "/" in page_slug or "\\" in page_slug:
            return abort(404)
        help_dir = (Path(__file__).parent / "help").resolve()
        help_path = (help_dir / (page_slug + ".md")).resolve()
        # Ensure resolved path is within help directory
        # Note: With whitelist check above, this is unreachable (defense-in-depth)
        if not help_path.is_relative_to(help_dir):  # pragma: no cover
            return abort(404)
        contents = help_path.read_text(encoding="utf-8")
        html = markdown(
            contents,
            extras=["fenced-code-blocks", "tables", "header-ids"],
        )
        return render_template(
            "help.html",
            page_slug=page_slug,
            help_html=Markup(  # noqa: S704
                render_template_string(
                    html,
                    rustfava_version=version("rustfava"),
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
        return lang or request.accept_languages.best_match(["en", *LOCALES])

    Babel(fava_app, locale_selector=_get_locale)  # type: ignore[no-untyped-call]


def create_app(
    files: Iterable[Path | str],
    *,
    load: bool = False,
    incognito: bool = False,
    read_only: bool = False,
    poll_watcher: bool = False,
) -> Flask:
    """Create a rustfava Flask application.

    Arguments:
        files: The list of Beancount files (paths).
        load: Whether to load the Beancount files directly.
        incognito: Whether to run in incognito mode.
        read_only: Whether to run in read-only mode.
        poll_watcher: Whether to use old poll watcher
    """
    fava_app = Flask("rustfava")
    fava_app.register_blueprint(json_api, url_prefix="/<bfile>/api")
    fava_app.json = RustfavaJSONProvider(fava_app)
    fava_app.app_ctx_globals_class = Context  # type: ignore[assignment]
    _setup_template_config(fava_app, incognito=incognito)
    _setup_babel(fava_app)
    _setup_filters(fava_app, read_only=read_only)
    _setup_routes(fava_app)

    fava_app.config["HAVE_EXCEL"] = HAVE_EXCEL
    fava_app.config["BEANCOUNT_FILES"] = [str(f) for f in files]
    fava_app.config["INCOGNITO"] = incognito
    fava_app.config["LEDGERS"] = _LedgerSlugLoader(
        fava_app, load=load, poll_watcher=poll_watcher
    )

    return fava_app


#: This is still provided for compatibility but will be removed at some point.
app = create_app([])
