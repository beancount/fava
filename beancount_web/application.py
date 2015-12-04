# -*- coding: utf-8 -*-
import sys

from datetime import date

from flask import Flask, render_template, url_for, request, redirect
from flask.helpers import locked_cached_property

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from livereload import Server, shell

from beancount_web.api import BeancountReportAPI

app = Flask(__name__)

@app.route('/account/<name>/')
def account(name=None):
    # if not account:
    #     redirect to index
    account = app.api.account(name=name)
    chart_data = []

    for journal_entry in account['journal']:
        if 'balance' in journal_entry.keys():
            for balance in journal_entry['balance']:
                chart_data.append((journal_entry['date'], balance['number']))  # TODO fix multi currency accounts

    return render_template('account.html', account=account, chart_data=chart_data)

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
    return render_template('balance_sheet.html', balance_sheet=balance_sheet)

@app.route('/income_statement/')
def income_statement():
    income_statement = app.api.income_statement()
    return render_template('income_statement.html', income_statement=income_statement)

@app.route('/trial_balance/')
def trial_balance():
    trial_balance = app.api.trial_balance()
    return render_template('trial_balance.html', trial_balance=trial_balance)

@app.route('/holdings/')
def holdings():
    holdings = app.api.holdings()
    return render_template('holdings.html', holdings=holdings)

@app.route('/net_worth/')
def net_worth():
    net_worth = app.api.net_worth()
    return render_template('net_worth.html', net_worth=net_worth)

@app.route('/errors/')
def errors():
    return render_template('errors.html') # errors are globally added

@app.route('/context/<ehash>/')
def context(ehash=None):
    context = app.api.context(ehash)
    context['context_highlighted'] = _hightlight(context['context'])
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

@app.context_processor
def utility_processor():
    def account_level(account_full):
        return account_full.count(":")+1
    return dict(account_level=account_level)

@app.context_processor
def inject_errors():
    return dict(errors=app.api.errors(),
                title=app.api.title(),
                active_years=app.api.active_years(),
                active_tags=app.api.active_tags(),
                active_components=app.api.active_components())

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

def _hightlight(source, hl_lines=[]):
    lexer = get_lexer_by_name("beancount", stripall=True)
    formatter = HtmlFormatter(linenos=True, lineanchors='line', anchorlinenos=True, hl_lines=hl_lines)
    return highlight(source, lexer, formatter)

def reload_beancount_file():
    app.api.reload()

def run(beancount_file, port=5000, host='localhost', debug=True):
    app.beancount_file = beancount_file
    app.filter_year = None
    app.filter_tag = None

    app.api = BeancountReportAPI(app.beancount_file)

    server = Server(app.wsgi_app)
    server.watch(app.beancount_file, reload_beancount_file)
    server.serve(port=port, host=host, debug=debug)
    # app.run(host, port, debug)

if __name__ == '__main__':
    run(sys.argv[1])
