# -*- coding: utf-8 -*-
import json
import decimal

from datetime import date, datetime

from flask import Flask, render_template, url_for, request, redirect, abort, Markup

app = Flask(__name__)

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

@app.route('/context/<ehash>/')
def context(ehash=None):
    context = app.api.context(ehash)
    # TODO handle errors
    return render_template('context.html', context=context)

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
            'journal',
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
    if isinstance(value, decimal.Decimal):
        return ("{:,." + str(digits) + "f}").format(value)
    return ''

@app.template_filter('last_segment')
def last_segment(account):
    return account.split(':')[-1]

class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, frozenset):
            return list(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

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
    return dict(account_level=account_level)


@app.context_processor
def inject_errors():
    options = app.api.options
    return dict(errors=app.api.errors,
                api=app.api,
                options=options,
                title=app.api.title,
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'])

@app.before_request
def perform_global_filters():
    year = request.args.get('filter_year', None)
    if year: year = int(year)

    tag = request.args.get('filter_tag', None)

    if year != app.filter_year or tag != app.filter_tag:
        app.api.filter(year=year, tag=tag)

    if year != app.filter_year:
        app.filter_year = year

    if tag != app.filter_tag:
        app.filter_tag = tag

