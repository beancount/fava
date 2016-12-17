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

from flask import (abort, Flask, flash, render_template, url_for, request,
                   redirect, send_from_directory, g, send_file, jsonify,
                   render_template_string)
from flask_babel import Babel
import markdown2
import werkzeug.urls
from werkzeug.utils import secure_filename
from beancount.core import amount, data
from beancount.core.number import D
from beancount.query import query_compile, query_parser
from beancount.scripts.format import align_beancount

from fava import template_filters, util
from fava.api import (BeancountReportAPI, FavaAPIException,
                      FavaFileNotFoundException)
from fava.api.file import insert_transaction
from fava.api.filters import FilterException
from fava.api.charts import BeanJSONEncoder
from fava.docs import HELP_PAGES
from fava.util import slugify, resource_path
from fava.util.excel import to_csv, to_excel, HAVE_EXCEL

app = Flask(__name__,  # pylint: disable=invalid-name
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

app.json_encoder = BeanJSONEncoder
app.jinja_options['extensions'].append('jinja2.ext.do')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# the key is currently only required to flash messages
app.secret_key = '1234'

app.config['HELP_DIR'] = resource_path('docs')
app.config['HAVE_EXCEL'] = HAVE_EXCEL
app.config['HELP_PAGES'] = HELP_PAGES
app.config['APIS'] = {}

REPORTS = [
    '_aside',
    'balance_sheet',
    'events',
    'errors',
    'holdings',
    'income_statement',
    'journal',
    'options',
    'statistics',
    'commodities',
    'editor',
    'trial_balance',
]


def load_file():
    """Load Beancount files. """
    for filepath in app.config['BEANCOUNT_FILES']:
        api = BeancountReportAPI(filepath)
        slug = slugify(api.options['title'])
        if not slug:
            slug = slugify(filepath)
        app.config['APIS'][slug] = api
    app.config['FILE_SLUGS'] = list(app.config['APIS'].keys())


BABEL = Babel(app)


@BABEL.localeselector
def get_locale():
    """Get locale.

    Returns:
        The locale that should be used for Babel. If not given as an option to
        Fava, guess from browser.

    """
    if app.config['language']:
        return app.config['language']
    return request.accept_languages.best_match(['de', 'en'])


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
    args = request.view_args.copy()
    args.update(kwargs)
    if app.config['use-external-editor']:
        if 'line' in args:
            return "beancount://%(file_path)s?lineno=%(line)d" % args
        else:
            return "beancount://%(file_path)s" % args
    else:
        args['report_name'] = 'editor'
        return url_for('report', **args)


@app.context_processor
def _template_context():
    """Inject variables into the global request context."""
    return {
        'api': g.api,
        'operating_currencies': g.api.options['operating_currency'],
        'datetime': datetime,
        'interval': request.args.get('interval', app.config['interval']),
    }


@app.before_request
def _perform_global_filters():
    if not g.api.options['operating_currency']:
        flash('No operating currency specified. '
              'Please add one to your beancount file.')

    g.filters = {
        name: request.args.get(name, None)
        for name in ['account', 'from', 'interval', 'payee', 'tag', 'time']
    }

    # check (and possibly reload) source file
    if request.endpoint != 'api_changed' and request.method == 'GET':
        g.api.changed()

    try:
        g.api.filter(**g.filters)
    except FilterException as exception:
        g.filters[exception.filter_type] = None
        flash(str(exception))


@app.url_defaults
def _inject_filters(endpoint, values):
    if 'bfile' in values or not getattr(g, 'beancount_file_slug', None):
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'bfile'):
        values['bfile'] = g.beancount_file_slug

    if endpoint in ['static', 'index']:
        return
    for filter_name in ['account', 'from', 'interval', 'payee', 'tag', 'time']:
        if filter_name not in values:
            values[filter_name] = g.filters[filter_name]


@app.url_value_preprocessor
def _pull_beancount_file(_, values):
    g.beancount_file_slug = values.pop('bfile', None) if values else None
    if not g.beancount_file_slug:
        g.beancount_file_slug = app.config['FILE_SLUGS'][0]
    if g.beancount_file_slug not in app.config['FILE_SLUGS']:
        abort(404)
    g.api = app.config['APIS'][g.beancount_file_slug]
    app.config.update(g.api.fava_options)


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
    assert subreport in ['journal', 'balances', 'changes']
    return render_template('account.html', account_name=name,
                           subreport=subreport)


@app.route('/<bfile>/document/', methods=['GET'])
def document():
    """Download a document."""
    file_path = request.args.get('file_path', None)
    try:
        document_path = g.api.document_path(file_path)
        directory = os.path.dirname(document_path)
        filename = os.path.basename(document_path)
        return send_from_directory(directory, filename)
    except FavaFileNotFoundException:
        return "File \"{}\" not found in entries.".format(file_path), 404


@app.route('/<bfile>/statement/', methods=['GET'])
def statement():
    """Download a statement file."""
    filename = request.args.get('filename', None)
    lineno = int(request.args.get('lineno', -1))
    key = request.args.get('key', None)
    try:
        document_path = g.api.statement_path(filename, lineno, key)
        directory = os.path.dirname(document_path)
        filename = os.path.basename(document_path)
        return send_from_directory(directory, filename)
    except FavaAPIException:
        return "Statement not found in entries.", 404
    except FavaFileNotFoundException:
        return "File not found.", 404


@app.route('/<bfile>/context/<ehash>/')
def context(ehash):
    """Show entry context."""
    return render_template('context.html', ehash=ehash)


@app.route('/<bfile>/holdings/by_<aggregation_key>/')
def holdings_by(aggregation_key):
    """The holdings report."""
    return render_template('holdings.html', aggregation_key=aggregation_key)


@app.route('/<bfile>/query/')
def query():
    """Run a query."""
    query_string = request.args.get('query_string', '')

    if not query_string:
        return render_template('query.html')

    try:
        types, rows = g.api.query(query_string)
    except (query_compile.CompilationError, query_parser.ParseError) as error:
        return render_template('query.html', error=error)

    return render_template('query.html', result_types=types, result_rows=rows)


@app.route('/<bfile>/<report_name>/')
def report(report_name):
    """Endpoint for most reports."""
    if report_name in REPORTS:
        return render_template('{}.html'.format(report_name))
    abort(404)


@app.route('/<bfile>/download-query/query_result.<result_format>')
@app.route('/<bfile>/download-query/<name>.<result_format>')
def download_query(result_format, name='query_result'):
    """Download a query result."""
    query_string = request.args.get('query_string', '')

    try:
        types, rows = g.api.query(query_string, numberify=True)
    except (query_compile.CompilationError, query_parser.ParseError):
        abort(400)

    filename = "{}.{}".format(secure_filename(name.strip()), result_format)

    if result_format == 'csv':
        data = to_csv(types, rows)
    else:
        if not app.config['HAVE_EXCEL']:
            abort(501)
        data = to_excel(types, rows, result_format, query_string)
    return send_file(data, as_attachment=True, attachment_filename=filename)


@app.route('/<bfile>/help/')
@app.route('/<bfile>/help/<string:page_slug>/')
def help_page(page_slug='_index'):
    """Fava's included documentation."""
    if page_slug not in app.config['HELP_PAGES']:
        abort(404)
    html = markdown2.markdown_path(
        os.path.join(app.config['HELP_DIR'], page_slug + '.md'),
        extras=['fenced-code-blocks', 'tables'])
    return render_template('help.html', page_slug=page_slug,
                           help_html=render_template_string(html))


def _api_error(message=''):
    return jsonify({'success': False, 'error': message})


def _api_success(**kwargs):
    kwargs['success'] = True
    return jsonify(kwargs)


@app.route('/<bfile>/api/changed/')
def api_changed():
    """Check for file changes."""
    return jsonify({'success': True, 'changed': g.api.changed()})


@app.route('/<bfile>/api/source/', methods=['GET', 'PUT'])
def api_source():
    """Read/write one of the source files."""
    if request.method == 'GET':
        try:
            data = g.api.source(request.args.get('file_path'))
            return _api_success(payload=data)
        except FavaAPIException as exception:
            return _api_error(exception.message)
    elif request.method == 'PUT':
        request.get_json()
        if request.get_json() is None:
            abort(400)
        g.api.set_source(request.get_json()['file_path'],
                         request.get_json()['source'])
        return _api_success()


@app.route('/<bfile>/api/format-source/', methods=['POST'])
def api_format_source():
    """Format beancount file."""
    request.get_json()
    if request.get_json() is None:
        abort(400)
    return _api_success(payload=align_beancount(request.get_json()['source']))


@app.route('/<bfile>/api/add-document/', methods=['PUT'])
def api_add_document():
    """Upload a document."""
    file = request.files['file']
    if file and len(g.api.options['documents']) > 0:
        target_folder_index = int(request.form['targetFolderIndex'])

        filepath = os.path.normpath(os.path.join(
            os.path.dirname(g.api.beancount_file_path),
            g.api.options['documents'][target_folder_index],
            request.form['account'].replace(':', '/'),
            secure_filename(request.form['filename']).replace('_', ' ')))

        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if os.path.isfile(filepath):
            return _api_error('{} already exists.'.format(filepath))

        file.save(filepath)

        if request.form.get('bfilename', None):
            try:
                g.api.insert_metadata(request.form['bfilename'],
                                      int(request.form['blineno']),
                                      'statement',
                                      os.path.basename(filepath))
            except FavaAPIException as exception:
                return _api_error(exception.message)
        return _api_success(message='Uploaded to {}'.format(filepath))
    return 'No file uploaded or no documents folder in options', 400


@app.route('/<bfile>/api/add-transaction/', methods=['PUT'])
def api_add_transaction():
    json = request.get_json()

    postings = []
    for posting in json['postings']:
        if posting['account'] not in g.api.all_accounts_active:
            return _api_error('Unknown account: {}.'
                              .format(posting['account']))
        number_ = D(posting['number']) if posting['number'] else None
        amount_ = amount.Amount(number_, posting.get('currency'))
        postings.append(data.Posting(posting['account'], amount_,
                                     None, None, None, None))

    if not postings:
        return _api_error('Transaction contains no postings.')

    date = util.date.parse_date(json['date'])[0]
    transaction = data.Transaction(
        None, date, json['flag'], json['payee'],
        json['narration'], None, None, postings)

    insert_transaction(transaction, g.api.source_files())
    return _api_success(message='Stored transaction.')


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

    redirect_url = url.replace(query=werkzeug.urls.url_encode(qs_dict,
                                                              sort=True))
    return redirect(werkzeug.urls.url_unparse(redirect_url))
