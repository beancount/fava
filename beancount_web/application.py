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

def account(account_name=None, with_journal=False, with_monthly_balances=False):
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
        monthly_balances = app.api.monthly_balances(account_name)
        monthly_treemaps = []
        # Only show three latest months
        max_months = int(request.args.get('months', 3))
        number_of_months = len(monthly_balances['months']) if len(monthly_balances['months']) < max_months else max_months

        for month_end in monthly_balances['months'][::-1][:number_of_months]:
            month_begin = date(month_end.year, month_end.month, 1)
            monthly_treemaps.append({
                'label': '{}'.format(month_end.strftime("%b '%y")),
                'month_begin': month_begin,
                'month_end': month_end,
                'balances': app.api.balances(account_name, begin_date=month_begin, end_date=month_end)
            })

        return render_template('account.html', account_name=account_name, monthly_balances=monthly_balances, monthly_treemaps=monthly_treemaps)

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

@app.route('/journal/')
def journal():
    if request.args.get('is_ajax', False):
        return jsonify({ 'data': app.api.journal() })
    else:
        return render_template('journal.html')

@app.route('/source/', methods=['GET', 'POST'])
def source():
    if request.method == "GET":
        if request.args.get('is_ajax', False):
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
    if isinstance(value, decimal.Decimal):
        return ("{:,." + str(digits) + "f}").format(value)
    return ''

@app.template_filter('last_segment')
def last_segment(account):
    return account.split(':')[-1]

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
    return dict(errors=app.api.errors,
                api=app.api,
                options=options,
                title=app.api.title,
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'],
                entry_filters=app.entry_filters)
