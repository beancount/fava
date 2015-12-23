# -*- coding: utf-8 -*-
import os
import json
import decimal

from datetime import date, datetime

from flask import Flask, render_template, url_for, request, redirect, abort, Markup, send_from_directory, jsonify
from flask.ext.assets import Environment, Bundle
from flask.json import JSONEncoder

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.entry_filters = {}

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

def account(account_name=None, with_journal=False, with_monthly_balances=False, with_yearly_balances=False):
    if with_journal:
        journal = app.api.journal(account_name, with_change_and_balance=True)

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
        return jsonify({ 'data': app.api.journal() })
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

@app.route('/filter/permalink/')
def filter_permalink():
    next_ = request.values.get('next', None)
    filter_types = request.values.getlist('filter_type')
    filter_values = request.values.getlist('filter_value')

    if len(filter_types) != len(filter_values):
        return "Invalid arguments: Lengths of filter types and filter values do not match", 400

    if len(list(ftype for ftype in filter_types if ftype == 'time')) > 1:
        return "Invalid arguments: Only one time filter allowed", 400

    if len(list(ftype for ftype in filter_types if ftype == 'account')) > 1:
        return "Invalid arguments: Only one account filter allowed", 400

    app.entry_filters['time'] = None
    app.entry_filters['account'] = None
    app.entry_filters['tags'] = set()
    app.entry_filters['payees'] = set()

    for index, type_ in enumerate(filter_types):
        if type_ in ['tags', 'payees']:
            app.entry_filters[type_].add(filter_values[index])
        if type_ in ['account', 'time']:
            app.entry_filters[type_] = filter_values[index]

    app.api.filter(time_str = app.entry_filters.get('time', None),
                    account = app.entry_filters.get('account', None),
                       tags = app.entry_filters.get('tags', set()).copy(),
                     payees = app.entry_filters.get('payees', set()).copy())

    return redirect(next_)

@app.route('/filter/', methods=['GET', 'POST'])
def filter_entries():
    type_ = request.values.get('filter_type', None)
    value = request.values.get('filter_value', None)
    next_ = request.values.get('next', None)

    if type_ and value and next_:
        remove = request.values.get('filter_remove', False)
        if remove and remove.lower() == 'true': remove = True
        else:                                   remove = False

        if type_ in ['time', 'account']:
            if remove:
                app.entry_filters.pop(type_, None)
            else:
                app.entry_filters[type_] = value

        if type_ in ['tags', 'payees']:
            if remove:
                if type_ in app.entry_filters:
                    if value in app.entry_filters[type_]:
                        app.entry_filters[type_].remove(value)
            else:
                if value == "" and app.entry_filters[type_]:
                    app.entry_filters.pop(type_, None)
                else:
                    if not type_ in app.entry_filters:
                        app.entry_filters[type_] = set()
                    app.entry_filters[type_].add(value)

        app.api.filter(time_str = app.entry_filters.get('time', None),
                        account = app.entry_filters.get('account', None),
                           tags = app.entry_filters.get('tags', set()).copy(),
                         payees = app.entry_filters.get('payees', set()).copy())

        return redirect(next_)

    return "Parameters missing", 400

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
    if 'green':  return "The latest posting is a balance check that passed (i.e., known-good)"
    if 'red':    return "The latest posting is a balance check that failed (i.e., known-bad)"
    if 'yellow': return "The latest posting is not a balance check (i.e., unknown)"
    if 'gray':   return "The account hasn't been updated in a while (as compared to the last available date in the file)"
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

@app.template_filter('filter_url')
def generate_filter_url(entry_filters):
    url_time    = "filter_type=time&filter_value={}&".format(entry_filters['time']) if 'time' in entry_filters and entry_filters['time'] else ''
    url_account = "filter_type=account&filter_value={}&".format(entry_filters['account']) if 'account' in entry_filters and entry_filters['account'] else ''
    url_tags    = "".join(list("filter_type=tags&filter_value={}&".format(tag) for tag in entry_filters['tags'])) if 'tags' in entry_filters else ''
    url_payees  = "".join(list("filter_type=payees&filter_value={}&".format(payee) for payee in entry_filters['payees'])) if 'payees' in entry_filters else ''
    return "{}{}{}{}next={}".format(url_time, url_account, url_tags, url_payees, request.path)

@app.context_processor
def utility_processor():
    def account_level(account_full):
        return account_full.count(":")+1
    return dict(account_level=account_level)

@app.context_processor
def inject_errors():
    options = app.api.options
    config  = app.user_config['beancount-web'] if app.user_config and 'beancount-web' in app.user_config else {}
    return dict(errors=app.api.errors,
                api=app.api,
                options=options,
                config=config,
                title=app.api.title,
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'],
                entry_filters=app.entry_filters)
