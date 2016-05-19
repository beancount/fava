# -*- coding: utf-8 -*-
import configparser
import os
from datetime import datetime
import markdown2

from flask import (abort, Flask, flash, render_template, url_for, request,
                   redirect, send_from_directory, g, send_file)
from flask.ext.babel import Babel
from werkzeug import secure_filename
from beancount.core.number import Decimal

from fava import config
from fava.api import BeancountReportAPI
from fava.api.filters import FilterException
from fava.api.serialization import BeanJSONEncoder
from fava.util import slugify, uniquify
from fava.util.excel import to_csv, to_excel, HAVE_EXCEL


app = Flask(__name__)
app.json_encoder = BeanJSONEncoder
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# the key is currently only required to flash messages
app.secret_key = '1234'

app.config['DEFAULT_SETTINGS'] = \
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 'default-settings.conf')
app.config['USER_SETTINGS'] = None
app.config['HELP_DIR'] = \
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')
app.config['HAVE_EXCEL'] = HAVE_EXCEL
app.config['APIS'] = {}


def load_file(beancount_file_slug=None):
    for filepath in app.config['BEANCOUNT_FILES']:
        api = BeancountReportAPI()
        api.load_file(filepath)
        slug = slugify(api.options['title'])
        app.config['APIS'][slug] = api
    app.config['FILE_SLUGS'] = list(app.config['APIS'].keys())


def load_settings():
    app.config.raw = configparser.ConfigParser()
    app.config.raw.read(app.config['DEFAULT_SETTINGS'])
    if app.config['USER_SETTINGS']:
        app.config.raw.read(app.config['USER_SETTINGS'])

    for option in config.bool_options:
        app.config[option] = app.config.raw.getboolean('fava', option)
    for option in config.int_options:
        app.config[option] = app.config.raw.getint('fava', option)
    for option in config.list_options:
        if app.config.raw.has_option('fava', option):
            app.config[option] = \
                app.config.raw.get('fava', option).strip().split("\n")
        else:
            app.config[option] = None
    for option in config.str_options:
        if app.config.raw.has_option('fava', option):
            app.config[option] = app.config.raw.get('fava', option)
        else:
            app.config[option] = None


def discover_help_pages():
    app.config['HELP_PAGES'] = {}
    for page in os.listdir(app.config['HELP_DIR']):
        html = markdown2.markdown_path(
            os.path.join(app.config['HELP_DIR'], page), extras=["metadata"])
        slug = os.path.splitext(os.path.basename(page))[0]
        title = html.metadata['title']

        app.config['HELP_PAGES'][slug] = title


load_settings()
discover_help_pages()

babel = Babel(app)


@babel.localeselector
def get_locale():
    if app.config['language']:
        return app.config['language']
    return request.accept_languages.best_match(['de', 'en'])


@app.route('/')
def root():
    return redirect(url_for('index', bfile=app.config['FILE_SLUGS'][0]))


@app.route('/<bfile>/')
def index():
    return redirect(url_for('report', report_name='income_statement'))


@app.route('/<bfile>/account/<name>/')
def account_with_journal(name=None):
    return render_template('account.html', account_name=name, journal=True)


@app.route('/<bfile>/account/<name>/balances/')
def account_with_interval_balances(name):
    return render_template('account.html', account_name=name, accumulate=True)


@app.route('/<bfile>/account/<name>/changes/')
def account_with_interval_changes(name):
    return render_template('account.html', account_name=name, accumulate=False)


@app.route('/<bfile>/document/', methods=['GET'])
def document():
    document_path = request.args.get('file_path', None)
    if document_path and g.api.is_valid_document(document_path):
        # metadata-statement-paths may be relative to the beancount-file
        if not os.path.isabs(document_path):
            document_path = os.path.join(os.path.dirname(
                os.path.realpath(g.api.beancount_file_path)), document_path)

        directory = os.path.dirname(document_path)
        filename = os.path.basename(document_path)
        return send_from_directory(directory, filename)
    else:
        return "File \"{}\" not found in entries.".format(document_path), 404


@app.route('/<bfile>/document/add/', methods=['POST'])
def add_document():
    file = request.files['file']
    if file and len(g.api.options['documents']) > 0:
        target_folder_index = int(request.form['targetFolderIndex'])
        target_folder = g.api.options['documents'][target_folder_index]

        filename = os.path.join(
            os.path.dirname(g.api.beancount_file_path),
            target_folder,
            request.form['account_name'].replace(':', '/').replace('..', ''),
            secure_filename(request.form['filename']))

        filepath = os.path.dirname(filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath, exist_ok=True)

        if os.path.isfile(filename):
            return "File \"{}\" already exists." \
                "Aborted document upload.".format(filename), 409

        file.save(filename)
        return "Uploaded to {}".format(filename), 200
    return "No file detected or no documents folder specified in options." \
           "Aborted document upload.", 424


@app.route('/<bfile>/context/<ehash>/')
def context(ehash=None):
    return render_template('context.html', ehash=ehash)


@app.route('/<bfile>/query/')
def query():
    name = request.args.get('name', 'query_result')
    result_format = request.args.get('result_format', 'html')
    query_string = request.args.get('query_string', '')
    numberify = bool(result_format != 'html')

    if not query_string:
        return render_template('query.html')

    try:
        types, rows = g.api.query(query_string, numberify)
    except Exception as e:
        return render_template('query.html', error=e)

    if result_format == 'html':
        return render_template('query.html', result_types=types,
                               result_rows=rows)
    else:
        filename = "{}.{}".format(secure_filename(name.strip()), result_format)

        if result_format == 'csv':
            fd = to_csv(types, rows)
        else:
            if not config['HAVE_EXCEL']:
                abort(501)
            fd = to_excel(types, rows, result_format, query_string)
        return send_file(fd, as_attachment=True, attachment_filename=filename)


@app.route('/<bfile>/help/')
@app.route('/<bfile>/help/<string:page_slug>/')
def help_page(page_slug='_index'):
    if page_slug not in app.config['HELP_PAGES'].keys():
        abort(404)
    html = markdown2.markdown_path(
        os.path.join(app.config['HELP_DIR'], page_slug + '.md'),
        extras=["metadata", "fenced-code-blocks", "tables"])
    return render_template('help.html', help_html=html, page_slug=page_slug)


@app.route('/<bfile>/journal/')
def journal():
    return render_template('journal.html')


@app.route('/<bfile>/source/', methods=['GET', 'POST'])
def source():
    if request.method == "GET":
        if request.is_xhr:
            requested_file_path = request.args.get('file_path', None)
            if requested_file_path in [app.config['USER_SETTINGS'],
                                       app.config['DEFAULT_SETTINGS']]:
                with open(requested_file_path, 'r') as f:
                    settings_file_content = f.read()
                return settings_file_content
            else:
                return g.api.source(file_path=requested_file_path)
        else:
            return render_template(
                'source.html',
                file_path=request.args.get('file_path',
                                           g.api.beancount_file_path))

    elif request.method == "POST":
        file_path = request.form['file_path']
        source = request.form['source']

        if file_path == app.config['USER_SETTINGS']:
            with open(file_path, 'w+', encoding='utf8') as f:
                f.write(source)
            successful = True
            load_settings()
        if file_path == app.config['DEFAULT_SETTINGS']:
            successful = False
        else:
            successful = g.api.set_source(file_path=file_path, source=source)
        return str(successful)


@app.route('/<bfile>/event/<event_type>/')
def event_details(event_type=None):
    return render_template('event_detail.html', event_type=event_type)


@app.route('/<bfile>/holdings/by_<aggregation_key>/')
def holdings_by(aggregation_key):
    return render_template('holdings.html', aggregation_key=aggregation_key)


@app.route('/<bfile>/<report_name>/')
def report(report_name):
    if report_name in [
            'balance_sheet',
            'documents',
            'notes',
            'events',
            'errors',
            'income_statement',
            'holdings',
            'options',
            'statistics',
            'commodities',
            'net_worth',
            'trial_balance',
    ]:
        return render_template('{}.html'.format(report_name))
    abort(404)


@app.template_filter()
def format_currency(value, currency=None, show_if_zero=False):
    if not value and not show_if_zero:
        return ''
    if value == 0.0:
        return g.api.quantize(Decimal(0.0), currency)
    return g.api.quantize(value, currency)


@app.template_filter()
def format_amount(amount):
    if not amount:
        return ''
    return "{} {}".format(format_currency(amount.number, amount.currency),
                          amount.currency)


@app.template_filter()
def last_segment(account):
    return account.split(':')[-1]


@app.template_filter()
def account_level(account_full):
    return account_full.count(":")+1


@app.template_filter()
def show_account(account):
    show_this_account = False
    if account['is_leaf']:
        show_this_account = True
        if not app.config['show-closed-accounts'] and \
                account['is_closed']:
            show_this_account = False
        if not app.config['show-accounts-with-zero-balance'] and \
                not account['balance']:
            show_this_account = False
        if not app.config['show-accounts-with-zero-transactions'] and \
                not account['has_transactions']:
            show_this_account = False
    return show_this_account or any(
        show_account(a) for a in account['children'])


@app.template_filter()
def basename(file_path):
    return os.path.basename(file_path)


@app.template_filter()
def should_collapse_account(account_name):
    if not app.config['collapse-accounts']:
        return False

    return account_name in app.config['collapse-accounts']


@app.template_filter()
def uptodate_eligible(account_name):
    key = 'fava-uptodate-indication'
    if key in g.api.account_open_metadata(account_name):
        return g.api.account_open_metadata(account_name)[key] == 'True'
    else:
        return False


@app.url_value_preprocessor
def pull_beancount_file(endpoint, values):
    g.beancount_file_slug = values.pop('bfile', None)
    if not g.beancount_file_slug:
        g.beancount_file_slug = app.config['FILE_SLUGS'][0]
    if g.beancount_file_slug not in app.config['FILE_SLUGS']:
        abort(404)
    g.api = app.config['APIS'][g.beancount_file_slug]


@app.context_processor
def template_context():
    def url_for_current(**kwargs):
        if not kwargs:
            return url_for(request.endpoint, **request.view_args)
        args = request.view_args.copy()
        args.update(kwargs)
        return url_for(request.endpoint, **args)

    def url_for_source(**kwargs):
        args = request.view_args.copy()
        args.update(kwargs)
        if app.config['use-external-editor']:
            if 'line' in args:
                return "beancount://%(file_path)s?lineno=%(line)d" % args
            else:
                return "beancount://%(file_path)s" % args
        else:
            return url_for('source', **args)

    return dict(url_for_current=url_for_current,
                url_for_source=url_for_source,
                api=g.api,
                operating_currencies=g.api.options['operating_currency'],
                today=datetime.now().strftime('%Y-%m-%d'),
                interval=request.args.get('interval',
                                          app.config['default-interval']),)


@app.url_defaults
def inject_filters(endpoint, values):
    if 'bfile' in values or not g.beancount_file_slug:
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'bfile'):
        values['bfile'] = g.beancount_file_slug

    if endpoint == 'static':
        return
    for filter in ['time', 'account', 'interval']:
        if filter not in values:
            values[filter] = g.filters[filter]
    for list_filter in ['tag', 'payee']:
        if list_filter in values:
            values[list_filter] = uniquify(values[list_filter])
        else:
            values[list_filter] = uniquify(g.filters[list_filter])
    if 'pop' in values:
        key, value = values['pop']
        values.pop('pop')
        values[key] = [v for v in g.filters[key] if v != value]


@app.before_request
def perform_global_filters():
    if 'operating_currency' not in g.api.options:
        flash('No operating currency specified. '
              'Please add one to your beancount file.')

    g.filters = {
        'time': request.args.get('time', None),
        'account': request.args.get('account', None),
        'tag': request.args.getlist('tag'),
        'payee': request.args.getlist('payee'),
        'interval': request.args.get('interval', None),
    }

    try:
        g.api.filter(**g.filters)
    except FilterException as e:
        g.filters['time'] = None
        flash(str(e))
