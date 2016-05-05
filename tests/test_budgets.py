from datetime import datetime as dt

from fava.api.budgets import Dateline
from fava.util.date import number_of_days_in_period

def test_budgets_dateline_daily():
    BUDGET = 2.5
    dl = Dateline(dt(2016, 5, 1), 'daily', BUDGET, 'EUR')

    assert dl.value(dt(2016, 5, 1)) == BUDGET
    assert dl.value(dt(2016, 9, 1)) == BUDGET
    assert dl.value(dt(2018, 12, 31)) == BUDGET


def test_budgets_dateline_weekly():
    BUDGET = 21
    dl = Dateline(dt(2016, 5, 1), 'weekly', BUDGET, 'EUR')

    assert dl.value(dt(2016, 5, 1)) == BUDGET / number_of_days_in_period('weekly', dt(2016, 5, 1))
    assert dl.value(dt(2016, 9, 1)) == BUDGET / number_of_days_in_period('weekly', dt(2016, 9, 1))
    assert dl.value(dt(2018, 12, 31)) == BUDGET / number_of_days_in_period('weekly', dt(2018, 12, 31))


def test_budgets_dateline_monthly():
    BUDGET = 100
    dl = Dateline(dt(2016, 5, 1), 'monthly', BUDGET, 'EUR')

    assert dl.value(dt(2016, 1, 1)) == BUDGET / number_of_days_in_period('monthly', dt(2016, 1, 1))
    assert dl.value(dt(2016, 2, 1)) == BUDGET / number_of_days_in_period('monthly', dt(2016, 2, 1))
    assert dl.value(dt(2018, 3, 31)) == BUDGET / number_of_days_in_period('monthly', dt(2016, 3, 31))


def test_budgets_dateline_quarterly():
    BUDGET = 123456.7
    dl = Dateline(dt(2016, 1, 1), 'quarterly', BUDGET, 'EUR')

    assert dl.value(dt(2016, 2, 1)) == BUDGET / number_of_days_in_period('quarterly', dt(2016, 2, 1))
    assert dl.value(dt(2016, 5, 30)) == BUDGET / number_of_days_in_period('quarterly', dt(2016, 5, 30))
    assert dl.value(dt(2016, 8, 15)) == BUDGET / number_of_days_in_period('quarterly', dt(2016, 8, 15))
    assert dl.value(dt(2016, 11, 15)) == BUDGET / number_of_days_in_period('quarterly', dt(2016, 11, 15))


def test_budgets_dateline_yearly():
    BUDGET = 99999.87
    dl = Dateline(dt(2010, 1, 1), 'yearly', BUDGET, 'EUR')

    assert dl.value(dt(2011, 2, 1)) == BUDGET / number_of_days_in_period('yearly', dt(2011, 2, 1))
    assert dl.value(dt(2015, 5, 30)) == BUDGET / number_of_days_in_period('yearly', dt(2015, 5, 30))
    assert dl.value(dt(2016, 8, 15)) == BUDGET / number_of_days_in_period('yearly', dt(2016, 8, 15))


# @pytest.fixture
# def setup_app(tmpdir):
#     filename = tmpdir.join('beancount_budget.example')
#     with filename.open('w') as fd:
#         today = dt.date.today()
#         write_example_file(dt.date(1980, 5, 12),
#                            dt.date(today.year - 3, 1, 1),
#                            today, True, fd)
#         write('2010-01-01 open Expenses:Books\n')
#         write('2010-01-01 * "" ""\n  Expenses:Books  10.00 EUR\n  Assets:Cash\n')  # noqa
#         write('2010-01-01 custom "budget" Expenses:Books "monthly"  20.00 EUR\n')  # noqa
#         write('2014-05-01 * "" ""\n  Expenses:Books  10.00 EUR\n  Assets:Cash\n')  # noqa
#         write('2014-06-01 custom "budget" Expenses:Books "daily"  3.00 EUR\n')     # noqa
#     app.beancount_filename = str(filename)
#     api.load_file(app.beancount_filename)
#     app.testing = True
#
# def test_budget(setup_app):
    # app.api.budgets.budget(self, account_name, date_from, date_to):
