from datetime import datetime

from fava.api.budgets import Dateline


def test_budgets_dateline_daily():
    BUDGET = 2.5
    dl = Dateline(datetime(2016, 5, 1), 'daily', BUDGET, 'EUR')

    assert dl.days(datetime(2016, 5, 1)) == 1
    assert dl.days(datetime(2016, 5, 2)) == 1
    assert dl.days(datetime(2016, 5, 31)) == 1

    assert dl.value(datetime(2016, 5, 1)) == BUDGET
    assert dl.value(datetime(2016, 9, 1)) == BUDGET
    assert dl.value(datetime(2018, 12, 31)) == BUDGET


def test_budgets_dateline_weekly():
    BUDGET = 21
    dl = Dateline(datetime(2016, 5, 1), 'weekly', BUDGET, 'EUR')

    assert dl.days(datetime(2016, 5, 1)) == 7
    assert dl.days(datetime(2016, 5, 2)) == 7
    assert dl.days(datetime(2016, 5, 31)) == 7

    assert dl.value(datetime(2016, 5, 1)) == BUDGET / dl.days(datetime(2016, 5, 1))
    assert dl.value(datetime(2016, 9, 1)) == BUDGET / dl.days(datetime(2016, 9, 1))
    assert dl.value(datetime(2018, 12, 31)) == BUDGET / dl.days(datetime(2018, 12, 31))


def test_budgets_dateline_monthly():
    BUDGET = 100
    dl = Dateline(datetime(2016, 5, 1), 'monthly', BUDGET, 'EUR')

    assert dl.days(datetime(2016, 5, 1)) == 31
    assert dl.days(datetime(2016, 5, 2)) == 31
    assert dl.days(datetime(2016, 5, 31)) == 31

    assert dl.days(datetime(2016, 6, 1)) == 30
    assert dl.days(datetime(2016, 6, 15)) == 30
    assert dl.days(datetime(2016, 6, 30)) == 30

    assert dl.days(datetime(2016, 7, 1)) == 31
    assert dl.days(datetime(2016, 7, 15)) == 31
    assert dl.days(datetime(2016, 7, 31)) == 31

    assert dl.days(datetime(2016, 1, 1)) == 31
    assert dl.days(datetime(2016, 2, 1)) == 29
    assert dl.days(datetime(2016, 3, 31)) == 31

    assert dl.value(datetime(2016, 1, 1)) == BUDGET / dl.days(datetime(2016, 1, 1))
    assert dl.value(datetime(2016, 2, 1)) == BUDGET / dl.days(datetime(2016, 2, 1))
    assert dl.value(datetime(2018, 3, 31)) == BUDGET / dl.days(datetime(2016, 3, 31))


def test_budgets_dateline_quarterly():
    BUDGET = 123456.7
    dl = Dateline(datetime(2016, 1, 1), 'quarterly', BUDGET, 'EUR')

    assert dl.days(datetime(2016, 2, 1)) == 90
    assert dl.days(datetime(2016, 5, 30)) == 92
    assert dl.days(datetime(2016, 8, 15)) == 92
    assert dl.days(datetime(2016, 11, 15)) == 92

    assert dl.value(datetime(2016, 2, 1)) == BUDGET / dl.days(datetime(2016, 2, 1))
    assert dl.value(datetime(2016, 5, 30)) == BUDGET / dl.days(datetime(2016, 5, 30))
    assert dl.value(datetime(2016, 8, 15)) == BUDGET / dl.days(datetime(2016, 8, 15))
    assert dl.value(datetime(2016, 11, 15)) == BUDGET / dl.days(datetime(2016, 11, 15))


def test_budgets_dateline_yearly():
    BUDGET = 99999.87
    dl = Dateline(datetime(2010, 1, 1), 'yearly', BUDGET, 'EUR')

    assert dl.days(datetime(2011, 2, 1)) == 365
    assert dl.days(datetime(2015, 5, 30)) == 365
    assert dl.days(datetime(2016, 8, 15)) == 366

    assert dl.value(datetime(2011, 2, 1)) == BUDGET / dl.days(datetime(2011, 2, 1))
    assert dl.value(datetime(2015, 5, 30)) == BUDGET / dl.days(datetime(2015, 5, 30))
    assert dl.value(datetime(2016, 8, 15)) == BUDGET / dl.days(datetime(2016, 8, 15))


# @pytest.fixture
# def setup_app(tmpdir):
#     filename = tmpdir.join('beancount_budget.example')
#     with filename.open('w') as fd:
#         today = datetime.date.today()
#         write_example_file(datetime.date(1980, 5, 12),
#                            datetime.date(today.year - 3, 1, 1),
#                            today, True, fd)
#         write('2010-01-01 open Expenses:Books\n')
#         write('2010-01-01 * "" ""\n  Expenses:Books  10.00 EUR\n  Assets:Cash\n')
#         write('2010-01-01 custom "budget" Expenses:Books "monthly"  20.00 EUR\n')
#         write('2014-05-01 * "" ""\n  Expenses:Books  10.00 EUR\n  Assets:Cash\n')
#         write('2014-06-01 custom "budget" Expenses:Books "daily"  3.00 EUR\n')
#     app.beancount_filename = str(filename)
#     api.load_file(app.beancount_filename)
#     app.testing = True
#
# def test_budget(setup_app):
    # app.api.budgets.budget(self, account_name, date_from, date_to):
