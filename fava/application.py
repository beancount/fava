"""Fava's main WSGI application.

when using Fava's WSGI app, make sure to set ``app.config['BEANCOUNT_FILES']``
and call :func:`load_file` before starting the server.  To start a simple
server::

    from fava.application import app, load_file
    app.config['BEANCOUNT_FILES'] = ['/path/to/file.beancount']
    load_file()
    app.run('localhost', 5000)

Attributes:
    app: An instance of :class:`flask.Flask`, this is Fava's WSGI application.

"""
import datetime
import inspect
import os
from io import BytesIO

from flask import (abort, Flask, flash, render_template, url_for, request,
                   redirect, g, send_file, render_template_string)
from flask_babel import Babel
import markdown2
import werkzeug.urls
from werkzeug.utils import secure_filename
from beancount.utils.text_utils import replace_numbers
from beancount.core.data import Document

from fava import template_filters
from fava.core import FavaLedger
from fava.core.charts import FavaJSONEncoder
from fava.core.helpers import FavaAPIException, FilterException
from fava.help import HELP_PAGES
from fava.json_api import json_api
from fava.util import slugify, resource_path, setup_logging
from fava.util.excel import HAVE_EXCEL


setup_logging()
app = Flask(  # pylint: disable=invalid-name
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static'))
app.register_blueprint(json_api, url_prefix='/<bfile>/api')

app.json_encoder = FavaJSONEncoder
app.jinja_options['extensions'].append('jinja2.ext.do')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# the key is currently only required to flash messages
app.secret_key = '1234'

app.config['HAVE_EXCEL'] = HAVE_EXCEL
app.config['HELP_PAGES'] = HELP_PAGES
app.config['LEDGERS'] = {}

REPORTS = [
    '_context',
    'balance_sheet',
    'commodities',
    'events',
    'editor',
    'errors',
    'extract',
    'holdings',
    'import',
    'income_statement',
    'journal',
    'options',
    'query',
    'statistics',
    'trial_balance',
]


def load_file():
    """Load Beancount files. """
    for filepath in app.config['BEANCOUNT_FILES']:
        ledger = FavaLedger(filepath)
        slug = slugify(ledger.options['title'])
        if not slug:
            slug = slugify(filepath)
        app.config['LEDGERS'][slug] = ledger
    app.config['FILE_SLUGS'] = list(app.config['LEDGERS'].keys())


BABEL = Babel(app)


@BABEL.localeselector
def get_locale():
    """Get locale.

    Returns:
        The locale that should be used for Babel. If not given as an option to
        Fava, guess from browser.

    """
    if g.ledger.fava_options['language']:
        return g.ledger.fava_options['language']
    return request.accept_languages.best_match(
        ['de', 'en', 'es', 'zh', 'nl', 'fr', 'pt'])


for _, function in inspect.getmembers(template_filters, inspect.isfunction):
    app.add_template_filter(function)


@app.template_global()
def url_for_current(**kwargs):
    """URL for current page with updated request args."""
    if not kwargs:
        return url_for(request.endpoint, **request.view_args)
    args = request.view_args.copy()
    args.update(kwargs)
    return url_for(request.endpoint, **args)


@app.template_global()
def url_for_source(**kwargs):
    """URL to source file (possibly link to external editor)."""
    if g.ledger.fava_options['use-external-editor']:
        return "beancount://{}?lineno={}".format(
            kwargs.get('file_path'), kwargs.get('line', 1))
    return url_for('report', report_name='editor', **kwargs)


@app.context_processor
def _template_context():
    """Inject variables into the global request context."""
    return {
        'ledger': g.ledger,
        'operating_currencies': g.ledger.options['operating_currency'],
        'datetime': datetime,
        'interval': request.args.get('interval',
                                     g.ledger.fava_options['interval']),
    }


@app.before_request
def _perform_global_filters():
    g.filters = {
        name: request.args.get(name)
        for name in ['account', 'from', 'payee', 'tag', 'time']
    }

    # check (and possibly reload) source file
    if request.blueprint != 'json_api':
        g.ledger.changed()

    try:
        g.ledger.filter(**g.filters)
    except FilterException as exception:
        g.filters[exception.filter_type] = None
        flash(str(exception))


@app.after_request
def _incognito(response):
    """Replace all numbers with 'X'."""
    if (app.config.get('INCOGNITO') and
            response.content_type.startswith('text/html')):
        is_editor = (request.endpoint == 'report' and
                     request.view_args['report_name'] == 'editor')
        if not is_editor:
            original_text = response.get_data(as_text=True)
            response.set_data(replace_numbers(original_text))
    return response


@app.url_defaults
def _inject_filters(endpoint, values):
    if 'bfile' in values or not getattr(g, 'beancount_file_slug', None):
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'bfile'):
        values['bfile'] = g.beancount_file_slug

    if endpoint in ['static', 'index']:
        return
    if 'interval' not in values:
        values['interval'] = request.args.get('interval')
    if 'conversion' not in values:
        values['conversion'] = request.args.get('conversion')
    for filter_name in ['account', 'from', 'payee', 'tag', 'time']:
        if filter_name not in values:
            values[filter_name] = g.filters[filter_name]


@app.url_value_preprocessor
def _pull_beancount_file(_, values):
    g.beancount_file_slug = values.pop('bfile', None) if values else None
    if not g.beancount_file_slug:
        g.beancount_file_slug = app.config['FILE_SLUGS'][0]
    if g.beancount_file_slug not in app.config['FILE_SLUGS']:
        abort(404)
    g.ledger = app.config['LEDGERS'][g.beancount_file_slug]
    g.conversion = request.args.get('conversion')
    if not request.args.get('show'):
        g.journal_show = set(
            g.ledger.fava_options['journal-show'] +
            g.ledger.fava_options['journal-show-transaction'] +
            g.ledger.fava_options['journal-show-document'])
    else:
        g.journal_show = set(request.args.getlist('show'))


@app.errorhandler(FavaAPIException)
def fava_api_exception(error):
    """Handle API errors."""
    return error.message, 400


@app.route('/')
def root():
    """Redirect to the index page for the first Beancount file."""
    return redirect(url_for('index', bfile=app.config['FILE_SLUGS'][0]))


@app.route('/<bfile>/')
def index():
    """Redirect to the Income Statement."""
    return redirect(url_for('report', report_name='income_statement'))


@app.route('/<bfile>/account/<name>/')
@app.route('/<bfile>/account/<name>/<subreport>/')
def account(name, subreport='journal'):
    """The account report."""
    if subreport in ['journal', 'balances', 'changes']:
        return render_template(
            'account.html', account_name=name, subreport=subreport)
    abort(404)


@app.route('/<bfile>/document/', methods=['GET'])
def document():
    """Download a document."""
    filename = request.args.get('filename')
    if not any((filename == document.filename for document in
                g.ledger.all_entries_by_type[Document])):
        abort(404)
    return send_file(filename)


@app.route('/<bfile>/statement/', methods=['GET'])
def statement():
    """Download a statement file."""
    entry_hash = request.args.get('entry_hash')
    key = request.args.get('key')
    document_path = g.ledger.statement_path(entry_hash, key)
    return send_file(document_path)


@app.route('/<bfile>/holdings/by_<aggregation_key>/')
def holdings_by(aggregation_key):
    """The holdings report."""
    if aggregation_key in ['account', 'currency', 'cost_currency']:
        return render_template(
            'holdings.html', aggregation_key=aggregation_key)
    abort(404)


@app.route('/<bfile>/<report_name>/')
def report(report_name):
    """Endpoint for most reports."""
    if report_name in REPORTS:
        return render_template('{}.html'.format(report_name))
    abort(404)


@app.route('/<bfile>/download-query/query_result.<result_format>')
def download_query(result_format):
    """Download a query result."""
    name, data = g.ledger.query_shell.query_to_file(
        request.args.get('query_string', ''), result_format)

    filename = "{}.{}".format(secure_filename(name.strip()), result_format)
    return send_file(data, as_attachment=True, attachment_filename=filename)


@app.route('/<bfile>/download-journal/')
def download_journal():
    """Download a Journal file."""
    filename = "journal_{}.beancount".format(datetime.datetime.now())
    data = BytesIO(bytes(render_template('beancount_file'), 'utf8'))
    return send_file(data, as_attachment=True, attachment_filename=filename)


@app.route('/<bfile>/help/')
@app.route('/<bfile>/help/<string:page_slug>/')
def help_page(page_slug='_index'):
    """Fava's included documentation."""
    if page_slug not in app.config['HELP_PAGES']:
        abort(404)
    html = markdown2.markdown_path(
        os.path.join(resource_path('help'), page_slug + '.md'),
        extras=['fenced-code-blocks', 'tables'])
    return render_template(
        'help.html',
        page_slug=page_slug,
        help_html=render_template_string(html))


@app.route('/jump')
def jump():
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

    redirect_url = url.replace(query=werkzeug.urls.url_encode(
        qs_dict, sort=True))
    return redirect(werkzeug.urls.url_unparse(redirect_url))
