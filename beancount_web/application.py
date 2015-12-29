# -*- coding: utf-8 -*-
import os
import json
import decimal
from datetime import date, datetime

from flask import Flask, flash, render_template, url_for, request, redirect, abort, Markup, send_from_directory, jsonify, g
from flask.ext.assets import Environment
from flask.json import JSONEncoder

from beancount_web.api import FilterException

app = Flask(__name__)
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
    return account(account_name=name, with_journal=True)

@app.route('/account/<name>/monthly_balances/')
def account_with_monthly_balances(name=None):
    return account(account_name=name, with_monthly_balances=True)

@app.route('/account/<name>/yearly_balances/')
def account_with_yearly_balances(name=None):
    return account(account_name=name, with_yearly_balances=True)

def account(account_name=None, with_journal=False, with_journal_children=None, with_monthly_balances=False, with_yearly_balances=False):
    if with_journal:
        if not with_journal_children:
            with_journal_children = app.user_config['beancount-web'].getboolean('journal-show-childentries')

        journal = app.api.journal(account_name, with_change_and_balance=True, with_journal_children=with_journal_children)

        # should this be done in the api?
        linechart_data = []
        for journal_entry in journal:
            if 'balance' in journal_entry.keys():
                linechart_data.append({
                    'date': journal_entry['date'],
                    'balance': journal_entry['balance'],
                    'change': journal_entry['change'],
                })

        return render_template('account.html', account_name=account_name, journal=journal, linechart_data=linechart_data)

    if with_monthly_balances:
        interval_balances = app.api.monthly_balances(account_name)
        interval_format_str = "%b '%y"
        interval_begin_date_lambda = lambda x: date(x.year, x.month, 1)

    if with_yearly_balances:
        interval_balances = app.api.yearly_balances(account_name)
        interval_format_str = "%Y"
        interval_begin_date_lambda = lambda x: date(x.year, 1, 1)

    if with_monthly_balances or with_yearly_balances:
        interval_treemaps = []
        max_intervals = int(request.args.get('interval_end_dates', 3)) # Only show three latest treemaps
        num_of_intervals = len(interval_balances['interval_end_dates']) if len(interval_balances['interval_end_dates']) < max_intervals else max_intervals

        for interval_end_date in interval_balances['interval_end_dates'][::-1][:num_of_intervals]:
            interval_begin_date = interval_begin_date_lambda(interval_end_date)
            interval_treemaps.append({
                'label': '{}'.format(interval_end_date.strftime(interval_format_str)),
                'balances': app.api.balances(account_name, begin_date=interval_begin_date, end_date=interval_end_date)
            })

        return render_template('account.html', account_name=account_name,
                                        interval_format_str=interval_format_str,
                                          interval_balances=interval_balances,
                                          interval_treemaps=interval_treemaps,
                                       with_yearly_balances=with_yearly_balances,
                                      with_monthly_balances=with_monthly_balances)
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
def query(bql=None):
    query = bql if bql else request.args.get('bql', None)
    error = None
    result = None

    if query:
        try:
            result = app.api.query(query)
        except Exception as e:
            result = None
            error = e

    return render_template('query.html', query=query, result=result, error=error)

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
    if isinstance(value, decimal.Decimal) or isinstance(value, float):
        return ("{:,." + str(digits) + "f}").format(value)
    return ''

@app.template_filter('last_segment')
def last_segment(account):
    return account.split(':')[-1]

@app.template_filter('uptodate_infotext')
def uptodate_infotext(status):
    if status == 'green':  return "The latest posting is a balance check that passed (i.e., known-good)"
    if status == 'red':    return "The latest posting is a balance check that failed (i.e., known-bad)"
    if status == 'yellow': return "The latest posting is not a balance check (i.e., unknown)"
    if status == 'gray':   return "The account hasn't been updated in a while (as compared to the last available date in the file)"
    print("Status '{}' unknown".format(status))
    return "Status '{}' unknown".format(status)

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)

app.json_encoder = MyJSONEncoder

@app.template_filter('to_json')
def to_json(json_object):
    return Markup(json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '), cls=MyJSONEncoder))

@app.template_filter('pp')
def pretty_print(json_object):
    # This filter is used only for debugging purposes
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    json_dump = to_json(json_object)
    lexer = get_lexer_by_name('python', stripall=True)
    formatter = HtmlFormatter(linenos=True, lineanchors='line', anchorlinenos=True)
    highlighted_source = highlight(json_dump, lexer, formatter)

    return Markup(highlighted_source)

@app.template_filter('last_segment')
def last_segment(account_name):
    return account_name.split(':')[-1]


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

    return dict(account_level=account_level,
                url_for_current=url_for_current,
                search_suggestions=search_suggestions,
                uptodate_eligible=uptodate_eligible)

@app.context_processor
def inject_errors():
    options = app.api.options
    config  = app.user_config['beancount-web']
    return dict(errors=app.api.errors,
                api=app.api,
                options=options,
                config=config,
                title=app.api.title,
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'])


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
