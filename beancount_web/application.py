# -*- coding: utf-8 -*-
import json
import decimal

from datetime import date, datetime

from flask import Flask, render_template, url_for, request, redirect

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


app = Flask(__name__)

@app.route('/account/<name>/')
def account(name=None):
    # if not account:
    #     redirect to index
    account = app.api.account(account_name=name)

    # should this be done in the api?
    chart_data = []
    for journal_entry in account['journal']:
        if 'balance' in journal_entry.keys():
            chart_data.append({
                'date': journal_entry['date'],
                'balance': journal_entry['balance'],
                'change': journal_entry['change'],
            })

    treemap = {
        'label': 'Subaccounts',
        'balances': app.api.balances(name),
        'modifier': 1  # TODO find out via API?
    }

    return render_template('account.html', account=account, chart_data=chart_data, treemap=treemap)

@app.route('/journal/')
def journal():
    journal = app.api.journal()
    return render_template('journal.html', journal=journal)

@app.route('/documents/')
def documents():
    documents = app.api.documents()
    return render_template('documents.html', documents=documents)

@app.route('/')
def index():
    return redirect(url_for('balance_sheet'))

@app.route('/balance_sheet/')
def balance_sheet():
    balance_sheet = app.api.balance_sheet()
    net_worth = app.api.net_worth()
    return render_template('balance_sheet.html', balance_sheet=balance_sheet, net_worth=net_worth)

@app.route('/income_statement/')
def income_statement():
    income_statement = app.api.income_statement()
    return render_template('income_statement.html', income_statement=income_statement)

# TODO currently only works for top-level accounts
@app.route('/monthly_balances/<account>/')
def monthly_balances(account=None):
    monthly_balances = app.api.monthly_balances(account)
    monthly_treetables = []
    # Only show three latest months
    number_of_months = len(monthly_balances['months']) if len(monthly_balances['months']) < 3 else 3

    for month_end in monthly_balances['months'][::-1][:3]:
        month_begin = date(month_end.year, month_end.month, 1)
        monthly_treetables.append({
            'label': '{}'.format(month_end.strftime("%b '%y")),
            'month_begin': month_begin,
            'month_end': month_end,
            'balances': app.api.balances(account, begin_date=month_begin, end_date=month_end)
        })

    return render_template('monthly_balances.html', account=account, balances=monthly_balances, treetables=monthly_treetables)

@app.route('/trial_balance/')
def trial_balance():
    trial_balance = app.api.trial_balance()
    treemap_balances = []
    treemap_balances.append({
        'label': app.api.options()['name_expenses'],
        'balances': app.api.balances(app.api.options()['name_expenses'])
    })
    treemap_balances.append({
        'label': app.api.options()['name_income'],
        'balances': app.api.balances(app.api.options()['name_income']),
        'modifier': -1
    })
    treemap_balances.append({
        'label': app.api.options()['name_assets'],
        'balances': app.api.balances(app.api.options()['name_assets'])
    })
    treemap_balances.append({
        'label': app.api.options()['name_equity'],
        'balances': app.api.balances(app.api.options()['name_equity']),
        'modifier': -1
    })
    treemap_balances.append({
        'label': app.api.options()['name_liabilities'],
        'balances': app.api.balances(app.api.options()['name_liabilities'])
    })

    return render_template('trial_balance.html', trial_balance=trial_balance, treemap_balances=treemap_balances)

@app.route('/holdings/')
def holdings():
    holdings = app.api.holdings()
    return render_template('holdings.html', holdings=holdings)

@app.route('/net_worth/')
def net_worth():
    net_worth = app.api.net_worth()
    return render_template('net_worth.html', net_worth=net_worth)


@app.route('/options/')
def options():
    return render_template('options.html') # options are globally added

@app.route('/errors/')
def errors():
    return render_template('errors.html') # errors are globally added

@app.route('/context/<ehash>/')
def context(ehash=None):
    context = app.api.context(ehash)

    for context_ in context['contexts']:
        context_['context_highlighted'] = _hightlight(context_['context'])

    # TODO handle errors
    return render_template('context.html', context=context)

@app.route('/source/')
def source():
    source = app.api.source()

    line = request.args.get('hl_line', None)
    if line:
        lines = [int(line)]
    else:
        lines = []

    source_highlighted = _hightlight(source, hl_lines=lines)
    return render_template('source.html', source=source_highlighted)

@app.template_filter('format_currency')
def format_currency(value):
    if value:   return "{:,.2f}".format(value)
    else:       return ''

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

@app.template_filter('pretty_print')
def pretty_print(json_object):
    json_dump = json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '), cls=MyJSONEncoder)
    return _hightlight(json_dump, language='python')

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
    options = app.api.options()
    return dict(errors=app.api.errors(),
                options=options,
                title=app.api.title(),
                active_years=app.api.active_years(),
                active_tags=app.api.active_tags(),
                active_components=app.api.active_components(),
                operating_currencies=options['operating_currency'],
                commodities=options['commodities'])

@app.before_request
def perform_global_filters():
    year = request.args.get('filter_year', None)
    if year: year = int(year)

    tag = request.args.get('filter_tag', None)

    if year != app.filter_year or tag != app.filter_tag:
        app.api.reload(year=year, tag=tag)

    if year != app.filter_year:
        app.filter_year = year

    if tag != app.filter_tag:
        app.filter_tag = tag

def _hightlight(source, language="beancount", hl_lines=[]):
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = HtmlFormatter(linenos=True, lineanchors='line', anchorlinenos=True, hl_lines=hl_lines)
    return highlight(source, lexer, formatter)
