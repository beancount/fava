# -*- coding: utf-8 -*-
import json
import decimal

from datetime import date, datetime

from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)

@app.route('/account/<name>/')
def account_with_journal(name=None):
    return account(account_name=name, with_journal=True)

@app.route('/account/<name>/monthly_balances/')
def account_with_monthly_balances(name=None):
    return account(account_name=name, with_monthly_balances=True)

def account(account_name=None, with_journal=False, with_monthly_balances=False):
    if with_journal:
        journal = app.api.journal(account_name)
        monthly_totals = app.api.monthly_totals(account_name)

        # should this be done in the api?
        linechart_data = []
        for journal_entry in journal:
            if 'balance' in journal_entry.keys():
                linechart_data.append({
                    'date': journal_entry['date'],
                    'balance': journal_entry['balance'],
                    'change': journal_entry['change'],
                })

        treemap_data = {
            'label': 'Subaccounts',
            'balances': app.api.balances(account_name),
            'modifier': 1  # TODO find out via API?
        }

        return render_template('account.html', account_name=account_name, journal=journal, linechart_data=linechart_data, monthly_totals=monthly_totals, treemap_data=treemap_data)

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
    assets = app.api.balances(app.api.options()['name_assets'])
    liabilities = app.api.balances(app.api.options()['name_liabilities'])
    equity = app.api.balances(app.api.options()['name_equity'])
    net_worth = app.api.net_worth()
    return render_template('balance_sheet.html', assets=assets, liabilities=liabilities, equity=equity, net_worth=net_worth)

@app.route('/income_statement/')
def income_statement():
    options = app.api.options()

    income = app.api.balances(options['name_income'])
    expenses = app.api.balances(options['name_expenses'])

    income_monthly_totals = app.api.monthly_totals(options['name_income'])
    expenses_monthly_totals = app.api.monthly_totals(options['name_expenses'])
    # TODO calls api.monthly_totals twice for income and expenses
    monthly_totals = app.api.monthly_income_expenses_totals()

    return render_template('income_statement.html', income=income, expenses=expenses, income_monthly_totals=income_monthly_totals, expenses_monthly_totals=expenses_monthly_totals, monthly_totals=monthly_totals)

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
    # TODO handle errors
    return render_template('context.html', context=context)

@app.route('/source/', methods=['GET', 'POST'])
def source():
    if request.method == "GET":
        if request.args.get('is_ajax', False):
            return app.api.source(file_path=request.args.get('file_path', None))
        else:
            return render_template('source.html', file_path=request.args.get('file_path', None))

    elif request.method == "POST":
        successful_write = app.api.set_source(file_path=request.form['file_path'], source=request.form['source'])
        if (successful_write):
            app.api.load_file()
        return str(successful_write)


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

@app.template_filter('pp')
def pretty_print(json_object):
    # This filter is used only for debugging purposes
    from flask import Markup
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    json_dump = json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '), cls=MyJSONEncoder)
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
    options = app.api.options()
    return dict(errors=app.api.errors(),
                options=options,
                title=app.api.title(),
                api=app.api,
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
        app.api.filter(year=year, tag=tag)

    if year != app.filter_year:
        app.filter_year = year

    if tag != app.filter_tag:
        app.filter_tag = tag

