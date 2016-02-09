# -*- coding: utf-8 -*-
import os
import json
import decimal
from datetime import date, datetime

from flask import Flask, flash, render_template, url_for, request, redirect, abort, Markup, send_from_directory, jsonify, g
from flask.ext.assets import Environment

from beancount_web.api import FilterException
from beancount_web.api.serialization import BeanJSONEncoder


app = Flask(__name__)
app.json_encoder = BeanJSONEncoder
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# the key is currently only required to flash messages
app.secret_key = '1234'

assets = Environment()
app.config['ASSETS_CACHE'] = False
app.config['ASSETS_DEBUG'] = False
app.config['ASSETS_MANIFEST'] = None
assets.init_app(app)


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

@app.route('/document/')
def document():
    document_path = request.args.get('file_path', None)

    if document_path and app.api.is_valid_document(document_path):
        if not os.path.isabs(document_path):  # metadata-statement-paths may be relative to the beancount-file
            document_path = os.path.join(os.path.dirname(os.path.realpath(app.beancount_file)), document_path)

        directory = os.path.dirname(document_path)
        filename = os.path.basename(document_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return "File \"{}\" not found in entries.".format(document_path), 404

@app.route('/context/<ehash>/')
def context(ehash=None):
    context = app.api.context(ehash)
    # TODO handle errors
    return render_template('context.html', context=context)

@app.route('/query/')
def query(bql=None, query_hash=None):
    query_hash = query_hash or request.args.get('query_hash', None)
    if query_hash:
        query = app.api.queries(query_hash=query_hash)['query_string'].strip()
    else:
        query = bql or request.args.get('bql')
    error = None
    result = None

    if query:
        try:
            result = app.api.query(query)
        except Exception as e:
            result = None
            error = e

    return render_template('query.html', query=query, result=result, query_hash=query_hash, error=error)

@app.route('/query/stored_queries/<string:stored_query_hash>')
def get_stored_query(stored_query_hash=None):
    bql = app.api.queries(query_hash=stored_query_hash)['query_string'].strip()
    if request.is_xhr:
        return bql
    else:
        return redirect(url_for('query', bql=bql, query_hash=stored_query_hash))

@app.route('/journal/')
def journal():
    if request.is_xhr:
        return jsonify({ 'data': app.api.journal(with_change_and_balance=app.user_config['beancount-web'].getboolean('journal-general-show-balances')) })
    else:
        return render_template('journal.html')

@app.route('/source/', methods=['GET', 'POST'])
def source():
    if request.method == "GET":
        if request.is_xhr:
            return app.api.source(file_path=request.args.get('file_path', None))
        else:
            return render_template('source.html', file_path=request.args.get('file_path', app.api.beancount_file_path))

    elif request.method == "POST":
        successful_write = app.api.set_source(file_path=request.form['file_path'], source=request.form['source'])
        if (successful_write):
            app.api.load_file()
        return str(successful_write)

@app.route('/event/<event_type>/')
def event_details(event_type=None):
    return render_template('event_detail.html', event_type=event_type)

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
    return redirect(url_for('report', report_name='balance_sheet'))


@app.template_filter('format_currency')
def format_currency(value, digits=2):
    if value:
        return ("{:,." + str(digits) + "f}").format(value)
    return ''


@app.template_filter('last_segment')
def last_segment(account):
    return account.split(':')[-1]


@app.context_processor
def utility_processor():
    def account_level(account_full):
        return account_full.count(":")+1

    def url_for_current(**kwargs):
        if not kwargs:
            return url_for(request.endpoint, **request.view_args)
        args = request.view_args.copy()
        args.update(kwargs)
        return url_for(request.endpoint, **args)

    def url_for_source(**kwargs):
        args = request.view_args.copy()
        args.update(kwargs)
        if app.user_config['beancount-web'].getboolean('use-external-editor'):
            if 'line' in args:
                return "beancount://%(file_path)s?lineno=%(line)d" % args
            else:
                return "beancount://%(file_path)s" % args
        else:
            return url_for('source', **args)

    def search_suggestions(field_name):
        if field_name == 'Time':
            return [
                'This Month',
                '2015-03',
                'March 2015',
                'Mar 2015',
                'Last Year',
                'Aug Last Year',
                '2010-10 - 2014',
                'Year to Date'
            ]
        else:
            return []

    def uptodate_eligible(account_name):
        if not 'uptodate-indicator-exclude-accounts' in app.user_config['beancount-web']:
            return False

        exclude_accounts = app.user_config['beancount-web']['uptodate-indicator-exclude-accounts'].strip().split("\n")

        if not (account_name.startswith(app.api.options['name_assets']) or
           account_name.startswith(app.api.options['name_liabilities'])):
           return False

        if account_name in exclude_accounts:
            return False

        if not account_name in [account['full_name'] for account in app.api.all_accounts_leaf_only]:
            return False

        return True

    if  'collapse-accounts' in app.user_config['beancount-web']:
        collapse_accounts = app.user_config['beancount-web']['collapse-accounts'].strip().split("\n")

    def should_collapse_account(account_name):
        if not 'collapse-accounts' in app.user_config['beancount-web']:
            return False

        return account_name in collapse_accounts

    return dict(account_level=account_level,
                url_for_current=url_for_current,
                url_for_source=url_for_source,
                search_suggestions=search_suggestions,
                uptodate_eligible=uptodate_eligible,
                should_collapse_account=should_collapse_account)

@app.context_processor
def inject_errors():
    options = app.api.options
    config = app.user_config['beancount-web']
    return dict(api=app.api,
                options=options,
                config=config,
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'],
                now=datetime.now().strftime('%Y-%m-%d'))


def uniquify(seq):
    """Removes duplicate items from a list whilst preserving order. """
    seen = set()
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
            values[list_filter] = uniquify(g.filters[list_filter] + [values[list_filter]])
        else:
            values[list_filter] = uniquify(g.filters[list_filter])
    if 'pop' in values:
        key, value = values['pop']
        values['pop'] = None
        values[key] = [v for v in g.filters[key] if v != value]
    if 'remove' in values:
        values[values['remove']] = []
        values['remove'] = None


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
