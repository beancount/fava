"""Fava's main WSGI application.

when using Fava's WSGI app, make sure to set ``app.config['BEANCOUNT_FILES']``.
To start a simple server::

    from fava.application import app
    app.config['BEANCOUNT_FILES'] = ['/path/to/file.beancount']
    app.run('localhost', 5000)

Attributes:
    app: An instance of :class:`flask.Flask`, this is Fava's WSGI application.

"""
import datetime
import functools
import threading
from io import BytesIO
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import flask
import markdown2  # type: ignore
import werkzeug.urls
from beancount import __version__ as beancount_version
from beancount.core.account import ACCOUNT_RE
from beancount.utils.text_utils import replace_numbers  # type: ignore
from flask import abort
from flask import Flask
from flask import redirect
from flask import render_template
from flask import render_template_string
from flask import request
from flask import send_file
from flask_babel import Babel  # type: ignore
from flask_babel import get_translations
from werkzeug.utils import secure_filename

from fava import __version__ as fava_version
from fava import LANGUAGES
from fava import template_filters
from fava.context import g
from fava.core import FavaLedger
from fava.core.charts import FavaJSONEncoder
from fava.core.documents import is_document_or_import_file
from fava.help import HELP_PAGES
from fava.helpers import FavaAPIException
from fava.json_api import json_api
from fava.serialisation import serialise
from fava.util import next_key
from fava.util import resource_path
from fava.util import send_file_inline
from fava.util import setup_logging
from fava.util import slugify
from fava.util.date import Interval
from fava.util.excel import HAVE_EXCEL


STATIC_FOLDER = resource_path("static")
setup_logging()
app = Flask(  # pylint: disable=invalid-name
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(STATIC_FOLDER),
)
app.register_blueprint(json_api, url_prefix="/<bfile>/api")

app.json_encoder = FavaJSONEncoder  # type: ignore
try:
    jinja_extensions = app.jinja_options.setdefault("extensions", [])
except TypeError:  # Flask <2
    jinja_extensions = app.jinja_options["extensions"]
jinja_extensions.append("jinja2.ext.do")
jinja_extensions.append("jinja2.ext.loopcontrols")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config["HAVE_EXCEL"] = HAVE_EXCEL
app.config["ACCOUNT_RE"] = ACCOUNT_RE

REPORTS = [
    "balance_sheet",
    "commodities",
    "documents",
    "events",
    "editor",
    "errors",
    "holdings",
    "import",
    "income_statement",
    "journal",
    "options",
    "query",
    "statistics",
    "trial_balance",
]


LOAD_FILE_LOCK = threading.Lock()


def ledger_slug(ledger: FavaLedger) -> str:
    """Generate URL slug for a ledger."""
    title_slug = slugify(ledger.options["title"])
    return title_slug or slugify(ledger.beancount_file_path)


def update_ledger_slugs(ledgers: List[FavaLedger]) -> None:
    """Update the dictionary mapping URL slugs to ledgers."""
    ledgers_by_slug: Dict[str, FavaLedger] = {}
    for ledger in ledgers:
        slug = ledger_slug(ledger)
        unique_key = next_key(slug, ledgers_by_slug)
        ledgers_by_slug[unique_key] = ledger
    app.config["LEDGERS"] = ledgers_by_slug


def _load_file() -> None:
    """Load Beancount files.

    This is run automatically on the first request.
    """
    ledgers = [
        FavaLedger(filepath) for filepath in app.config["BEANCOUNT_FILES"]
    ]
    update_ledger_slugs(ledgers)


def get_locale() -> Optional[str]:
    """Get locale.

    Returns:
        The locale that should be used for Babel. If not given as an option to
        Fava, guess from browser.
    """
    lang = g.ledger.fava_options["language"]
    if lang is not None:
        return lang
    return request.accept_languages.best_match(["en"] + LANGUAGES)


BABEL = Babel(app)
BABEL.localeselector(get_locale)


for function in template_filters.FILTERS:
    app.add_template_filter(function)  # type: ignore
app.add_template_filter(serialise)


@app.url_defaults
def _inject_filters(endpoint: str, values: Dict[str, Any]) -> None:
    if "bfile" not in values and app.url_map.is_endpoint_expecting(
        endpoint, "bfile"
    ):
        values["bfile"] = g.beancount_file_slug
    if endpoint in ["static", "index"]:
        return
    for name in ["conversion", "interval", "account", "filter", "time"]:
        if name not in values:
            values[name] = request.args.get(name)


def static_url(filename: str) -> str:
    """Return a static url with an mtime query string for cache busting."""
    file_path = STATIC_FOLDER / filename
    try:
        mtime = int(file_path.stat().st_mtime)
    except FileNotFoundError:
        mtime = 0
    return url_for("static", filename=filename, mtime=mtime)


CACHED_URL_FOR = functools.lru_cache(2048)(flask.url_for)


def url_for(endpoint: str, **values: Any) -> str:
    """A wrapper around flask.url_for that uses a cache."""
    _inject_filters(endpoint, values)
    return CACHED_URL_FOR(endpoint, **values)


def url_for_source(**kwargs: Any) -> str:
    """URL to source file (possibly link to external editor)."""
    if g.ledger.fava_options["use-external-editor"]:
        return (
            f"beancount://{kwargs.get('file_path')}"
            + f"?lineno={kwargs.get('line', 1)}"
        )
    return url_for("report", report_name="editor", **kwargs)


def translations() -> Any:
    """Get translations catalog."""
    # pylint: disable=protected-access
    return get_translations()._catalog


app.add_template_global(static_url, "static_url")  # type: ignore
app.add_template_global(datetime.date.today, "today")
app.add_template_global(url_for, "url_for")  # type: ignore
app.add_template_global(url_for_source, "url_for_source")
app.add_template_global(translations, "translations")


@app.context_processor
def template_context() -> Dict[str, Any]:
    """Inject variables into the template context."""
    return dict(ledger=g.ledger)


@app.before_request
def _perform_global_filters() -> None:
    ledger = getattr(g, "ledger", None)
    if ledger:
        # check (and possibly reload) source file
        if request.blueprint != "json_api":
            ledger.changed()

        ledger.filter(
            account=request.args.get("account"),
            filter=request.args.get("filter"),
            time=request.args.get("time"),
        )


@app.after_request
def _incognito(response: flask.wrappers.Response) -> flask.wrappers.Response:
    """Replace all numbers with 'X'."""
    if app.config.get("INCOGNITO") and response.content_type.startswith(
        "text/html"
    ):
        is_editor = (
            request.endpoint == "report"
            and request.view_args is not None
            and request.view_args["report_name"] == "editor"
        )
        if not is_editor:
            original_text = response.get_data(as_text=True)
            response.set_data(replace_numbers(original_text))
    return response


@app.url_value_preprocessor
def _pull_beancount_file(
    _: Optional[str], values: Optional[Dict[str, str]]
) -> None:
    g.beancount_file_slug = values.pop("bfile", None) if values else None
    with LOAD_FILE_LOCK:
        if not app.config.get("LEDGERS"):
            _load_file()
    if g.beancount_file_slug:
        if g.beancount_file_slug not in app.config["LEDGERS"]:
            if not any(
                g.beancount_file_slug == ledger_slug(ledger)
                for ledger in app.config["LEDGERS"].values()
            ):
                abort(404)
            # one of the file slugs changed, update the mapping
            update_ledger_slugs(app.config["LEDGERS"].values())
        g.ledger = app.config["LEDGERS"][g.beancount_file_slug]
        g.conversion = request.args.get("conversion", "at_cost")
        g.interval = Interval.get(request.args.get("interval", "month"))


@app.errorhandler(FavaAPIException)  # type: ignore
def fava_api_exception(error: FavaAPIException) -> str:
    """Handle API errors."""
    return render_template(
        "_layout.html", page_title="Error", content=error.message
    )


@app.route("/")
@app.route("/<bfile>/")
def index() -> werkzeug.wrappers.response.Response:
    """Redirect to the Income Statement (of the given or first file)."""
    if not g.beancount_file_slug:
        g.beancount_file_slug = next(iter(app.config["LEDGERS"]))
    index_url = url_for("index")
    default_path = app.config["LEDGERS"][g.beancount_file_slug].fava_options[
        "default-page"
    ]
    return redirect(f"{index_url}{default_path}")


@app.route("/<bfile>/account/<name>/")
@app.route("/<bfile>/account/<name>/<subreport>/")
def account(name: str, subreport: str = "journal") -> str:
    """The account report."""
    if subreport in ["journal", "balances", "changes"]:
        return render_template(
            "account.html", account_name=name, subreport=subreport
        )
    return abort(404)


@app.route("/<bfile>/document/", methods=["GET"])
def document() -> Any:
    """Download a document."""
    filename = request.args.get("filename")
    if filename is None:
        return abort(404)
    if is_document_or_import_file(filename, g.ledger):
        return send_file_inline(filename)
    return abort(404)


@app.route("/<bfile>/statement/", methods=["GET"])
def statement() -> Any:
    """Download a statement file."""
    entry_hash = request.args.get("entry_hash", "")
    key = request.args.get("key", "")
    document_path = g.ledger.statement_path(entry_hash, key)
    return send_file_inline(document_path)


@app.route("/<bfile>/holdings/by_<aggregation_key>/")
def holdings_by(aggregation_key: str) -> str:
    """The holdings report."""
    if aggregation_key in ["account", "currency", "cost_currency"]:
        return render_template(
            "_layout.html",
            active_page="holdings",
            aggregation_key=aggregation_key,
        )
    return abort(404)


@app.route("/<bfile>/_query_result/")
def query_result() -> str:
    """Query shell."""
    return render_template("_query_result.html")


@app.route("/<bfile>/<report_name>/")
def report(report_name: str) -> str:
    """Endpoint for most reports."""
    if report_name in REPORTS:
        return render_template("_layout.html", active_page=report_name)
    return abort(404)


@app.route("/<bfile>/extension/<report_name>/")
def extension_report(report_name: str) -> str:
    """Endpoint for extension reports."""
    try:
        template, extension = g.ledger.extensions.template_and_extension(
            report_name
        )
        content = render_template_string(template, extension=extension)
        return render_template(
            "_layout.html", content=content, page_title=extension.report_title
        )
    except LookupError:
        return abort(404)


@app.route("/<bfile>/download-query/query_result.<result_format>")
def download_query(result_format: str) -> Any:
    """Download a query result."""
    name, data = g.ledger.query_shell.query_to_file(
        request.args.get("query_string", ""), result_format
    )

    filename = f"{secure_filename(name.strip())}.{result_format}"
    try:
        return send_file(data, as_attachment=True, download_name=filename)
    except TypeError:  # Flask <2
        return send_file(
            data, as_attachment=True, attachment_filename=filename
        )


@app.route("/<bfile>/download-journal/")
def download_journal() -> Any:
    """Download a Journal file."""
    now = datetime.datetime.now().replace(microsecond=0)
    filename = f"journal_{now.isoformat()}.beancount"
    data = BytesIO(bytes(render_template("beancount_file"), "utf8"))
    try:
        return send_file(data, as_attachment=True, download_name=filename)
    except TypeError:  # Flask <2
        return send_file(
            data, as_attachment=True, attachment_filename=filename
        )


@app.route("/<bfile>/help/", defaults={"page_slug": "_index"})
@app.route("/<bfile>/help/<string:page_slug>")
def help_page(page_slug: str) -> str:
    """Fava's included documentation."""
    if page_slug not in HELP_PAGES:
        abort(404)
    html = markdown2.markdown_path(
        (resource_path("help") / (page_slug + ".md")),
        extras=["fenced-code-blocks", "tables", "header-ids"],
    )
    return render_template(
        "_layout.html",
        active_page="help",
        page_slug=page_slug,
        help_html=render_template_string(
            html,
            beancount_version=beancount_version,
            fava_version=fava_version,
        ),
        HELP_PAGES=HELP_PAGES,
    )


@app.route("/jump")
def jump() -> werkzeug.wrappers.response.Response:
    """Redirect back to the referer, replacing some parameters.

    This is useful for sidebar links, e.g. a link ``/jump?time=year``
    would set the time filter to `year` on the current page.

    When accessing ``/jump?param1=abc`` from
    ``/example/page?param1=123&param2=456``, this view should redirect to
    ``/example/page?param1=abc&param2=456``.

    """
    url = werkzeug.urls.url_parse(request.referrer)
    qs_dict = url.decode_query()
    for key, values in request.args.lists():
        if len(values) == 1 and values[0] == "":
            try:
                del qs_dict[key]
            except KeyError:
                pass
            continue
        qs_dict.setlist(key, values)

    redirect_url = url.replace(
        query=werkzeug.urls.url_encode(qs_dict, sort=True)
    )
    return redirect(werkzeug.urls.url_unparse(redirect_url))
