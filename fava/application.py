# -*- coding: utf-8 -*-
import configparser
import os
from datetime import datetime
import io

import markdown2

from flask import (abort, Flask, flash, render_template, url_for, request,
                   redirect, send_from_directory, g, make_response)
from werkzeug import secure_filename

import pyexcel
import pyexcel.ext.xls
import pyexcel.ext.xlsx
import pyexcel.ext.ods3

from fava.api import BeancountReportAPI, FilterException
from fava.api.serialization import BeanJSONEncoder


app = Flask(__name__)
app.json_encoder = BeanJSONEncoder
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# the key is currently only required to flash messages
app.secret_key = '1234'

app.api = BeancountReportAPI()

defaults_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'default-settings.conf')

def load_settings(user_settings_file_path=None):
    app.config.raw = configparser.ConfigParser()
    app.config.raw.read(defaults_file)

    app.config.user = app.config.raw['fava']
    app.config.user['file_defaults'] = defaults_file

    if user_settings_file_path:
        app.config.user['file_user'] = user_settings_file_path
        app.config.raw.read(app.config.user['file_user'])
    else:
        app.config.user['file_user'] = ''

    if app.config.user['file_user'] == '':
        app.config_file = app.config.user['file_defaults']
    else:
        app.config_file = app.config.user['file_user']

load_settings()

app.docs_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')

def list_help_pages():
    help_pages = []

    for page in os.listdir(app.docs_dir):
        html = markdown2.markdown_path(os.path.join(app.docs_dir, page), extras=["metadata"])
        slug = "help/%s" % (os.path.splitext(os.path.basename(page))[0])
        title = html.metadata['title']

        help_pages.append((slug, title, None))

    return sorted(help_pages, key=lambda x: x[1] == 'Index', reverse=True)

app.help_pages = list_help_pages()



@app.route('/account/<name>/')
def account_with_journal(name=None):
    return render_template('account.html', account_name=name)


@app.route('/account/<name>/<interval>ly_balances/')
def account_with_interval_balances(name, interval):
    return render_template('account.html', account_name=name,
                           interval=interval, accumulate=True)


@app.route('/account/<name>/<interval>ly_changes/')
def account_with_interval_changes(name, interval):
    return render_template('account.html', account_name=name,
                           interval=interval, accumulate=False)


@app.route('/')
def index():
    return redirect(url_for('report', report_name='income_statement'))


@app.route('/document/', methods=['GET'])
@app.route('/document/add/', methods=['POST'])
def document():
    if request.method == "GET":
        document_path = request.args.get('file_path', None)

        if document_path and app.api.is_valid_document(document_path):
            # metadata-statement-paths may be relative to the beancount-file
            if not os.path.isabs(document_path):
                document_path = os.path.join(os.path.dirname(
                    os.path.realpath(app.beancount_file)), document_path)

            directory = os.path.dirname(document_path)
            filename = os.path.basename(document_path)
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            return "File \"{}\" not found in entries.".format(document_path), 404
    else:
        file = request.files['file']
        if file and len(app.api.options['documents']) > 0: # and allowed_file(file.filename):
            # TOOD Probably it should ask to enter a date, if the document
            #      doesn't start with one, so you don't need to rename the
            #      documents in advance.
            filepath = os.path.join(os.path.dirname(app.beancount_file),
                                      app.api.options['documents'][0],
                                      request.form['account_name'].replace(':', '/').replace('..', ''),
                                      secure_filename(file.filename))
            file.save(filepath)

        return "Uploaded to %s" % (filepath), 200

@app.route('/context/<ehash>/')
def context(ehash=None):
    return render_template('context.html', ehash=ehash)

def object_to_string(type, value):
    if str(type) == "<class 'beancount.core.inventory.Inventory'>":
        return "/".join(["%s %s" % (position.units.number, position.units.currency) for position in value.cost()])
    elif str(type) == "<class 'beancount.core.position.Position'>":
        return "%s %s" % (value.units.number, value.units.currency)
    else:
        return str(value)

@app.route('/query/')
def query(bql=None, query_hash=None, result_format='html'):
    query_hash = request.args.get('query_hash', None)
    result_format = request.args.get('result_format', 'html')

    if query_hash:
        query = app.api.queries(query_hash=query_hash)['query_string'].strip()
    else:
        query = request.args.get('bql', '')
    error = None
    result = None

    if query:
        try:
            numberify = (request.path == '/query/result.csv')
            result = app.api.query(query, numberify=numberify)
        except Exception as e:
            result = None
            error = e

    if result_format != 'html':
        if query:
            if result:
                result_array = [["%s" % (name) for name, type_ in result[0]]]
                for row in result[1]:
                    result_array.append([object_to_string(header[1], row[idx]) for idx, header in enumerate(result[0])])
            else:
                result_array = [[error]]

            if result_format in ('xls', 'xlsx', 'ods'):
                book = pyexcel.Book({
                    'Results': result_array,
                    'Query':   [['Query'],[query]]
                })
                respIO = io.BytesIO()
                book.save_to_memory(result_format, respIO)
            else:
                respIO = pyexcel.save_as(array=result_array, dest_file_type=result_format)

            respIO.seek(0)
            response = make_response(respIO.read())
            response.headers["Content-Disposition"] = "attachment; filename=query_result.%s" % (result_format)
            return response
        else:
            return redirect(url_for('query'))

    return render_template('query.html', query=query, result=result,
                           query_hash=query_hash, error=error)


@app.route('/query/stored_queries/<string:stored_query_hash>')
def get_stored_query(stored_query_hash=None):
    bql = app.api.queries(query_hash=stored_query_hash)['query_string'].strip()
    if request.is_xhr:
        return bql
    else:
        return redirect(url_for('query', bql=bql,
                                query_hash=stored_query_hash))

@app.route('/help/')
@app.route('/help/<string:page_slug>/')
def help_page(page_slug='index'):
    html = markdown2.markdown_path(os.path.join(app.docs_dir, page_slug + '.md'), extras=["metadata", "fenced-code-blocks", "tables"])
    return render_template('help.html', help_html=html, page_slug=page_slug, help_pages=app.help_pages)

@app.route('/journal/')
def journal():
    return render_template('journal.html')


@app.route('/source/', methods=['GET', 'POST'])
def source():
    if request.method == "GET":
        if request.is_xhr:
            requested_file_path = request.args.get('file_path', None)
            if requested_file_path == app.config_file:
                with open(requested_file_path, 'r') as f:
                    settings_file_content = f.read()
                return settings_file_content
            else:
                return app.api.source(file_path=requested_file_path)
        else:
            return render_template('source.html', file_path=request.args.get('file_path', app.api.beancount_file_path))

    elif request.method == "POST":
        file_path = request.form['file_path']
        source = request.form['source']

        if file_path == app.config_file:
            if file_path != defaults_file:
                with open(file_path, 'w+', encoding='utf8') as f:
                    f.write(source)
            successful = True
        else:
            successful = app.api.set_source(file_path=file_path,
                                            source=source)
        if successful:
            app.api.load_file()
            load_settings(app.config_file)

        return str(successful)


@app.route('/event/<event_type>/')
def event_details(event_type=None):
    return render_template('event_detail.html', event_type=event_type)


@app.route('/holdings/by_<aggregation_key>/')
def holdings_by(aggregation_key):
    return render_template('holdings.html', aggregation_key=aggregation_key)


@app.route('/<report_name>/')
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
def format_currency(value, digits=2):
    if value:
        return ("{:,." + str(digits) + "f}").format(value)
    return ''


@app.template_filter()
def last_segment(account):
    return account.split(':')[-1]


@app.template_filter()
def account_level(account_full):
    return account_full.count(":")+1


@app.template_filter()
def basename(file_path):
    return os.path.basename(file_path)


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
        if app.config.user.getboolean('use-external-editor'):
            if 'line' in args:
                return "beancount://%(file_path)s?lineno=%(line)d" % args
            else:
                return "beancount://%(file_path)s" % args
        else:
            return url_for('source', **args)

    def uptodate_eligible(account_name):
        key = 'fava-uptodate-indication'
        if key in app.api.account_open_metadata(account_name):
            return app.api.account_open_metadata(account_name)[key] == 'True'
        else:
            return False

    if 'collapse-accounts' in app.config.user:
        collapse_accounts = app.config.user['collapse-accounts'].strip().split("\n")

    def should_collapse_account(account_name):
        if 'collapse-accounts' not in app.config.user:
            return False

        return account_name in collapse_accounts

    return dict(url_for_current=url_for_current,
                url_for_source=url_for_source,
                uptodate_eligible=uptodate_eligible,
                should_collapse_account=should_collapse_account,
                api=app.api,
                options=app.api.options,
                config_file=app.config_file,
                config_file_defaults=app.config.user['file_defaults'],
                operating_currencies=app.api.options['operating_currency'],
                today=datetime.now().strftime('%Y-%m-%d'))


def uniquify(seq):
    """Removes duplicate items from a list whilst preserving order. """
    seen = set()
    if not seq:
        return []
    return [x for x in seq if x not in seen and not seen.add(x)]


@app.url_defaults
def inject_filters(endpoint, values):
    if endpoint == 'static':
        return
    for filter in ['time', 'account']:
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
    g.filters = {
        'time': request.args.get('time', None),
        'account': request.args.get('account', None),
        'tag': request.args.getlist('tag'),
        'payee': request.args.getlist('payee'),
    }

    try:
        app.api.filter(**g.filters)
    except FilterException as e:
        g.filters['time'] = None
        flash(str(e))
