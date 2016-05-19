from datetime import date

from beancount.core.number import Decimal
from beancount.parser import parser

from fava.api.budgets import Budgets
from fava.util.date import number_of_days_in_period


def get_budgets(beancount_string):
    entries, errors, options_map = parser.parse_string(beancount_string,
                                                       dedent=True)
    return Budgets(entries)


def test_budgets_dateline_daily():
    BUDGET = Decimal(2.5)
    budgets = get_budgets('2016-05-01 custom "budget" Expenses:Books "daily"  {} EUR'.format(BUDGET))  # noqa

    assert budgets.budget('Expenses:Books', date(2016, 5, 1), date(2016, 5, 2))['EUR'] == BUDGET  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 5, 1), date(2016, 5, 3))['EUR'] == BUDGET * 2  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 9, 2), date(2016, 9, 3))['EUR'] == BUDGET  # noqa
    assert budgets.budget('Expenses:Books', date(2018, 12, 31), date(2019, 1, 1))['EUR'] == BUDGET  # noqa


def test_budgets_dateline_weekly():
    BUDGET = Decimal(21)
    budgets = get_budgets('2016-05-01 custom "budget" Expenses:Books "weekly"  {} EUR'.format(BUDGET))  # noqa

    assert budgets.budget('Expenses:Books', date(2016, 5, 1), date(2016, 5, 2))['EUR'] == BUDGET / number_of_days_in_period('weekly', date(2016, 5, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 9, 1), date(2016, 9, 2))['EUR'] == BUDGET / number_of_days_in_period('weekly', date(2016, 9, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2018, 12, 31), date(2019, 1, 1))['EUR'] == BUDGET / number_of_days_in_period('weekly', date(2018, 12, 31))  # noqa


def test_budgets_dateline_monthly():
    BUDGET = Decimal(100)
    budgets = get_budgets('2014-05-01 custom "budget" Expenses:Books "monthly"  {} EUR'.format(BUDGET))  # noqa

    assert budgets.budget('Expenses:Books', date(2016, 1, 1), date(2016, 1, 2))['EUR'] == BUDGET / number_of_days_in_period('monthly', date(2016, 1, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 2, 1), date(2016, 2, 2))['EUR'] == BUDGET / number_of_days_in_period('monthly', date(2016, 2, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2018, 3, 31), date(2018, 4, 1))['EUR'] == BUDGET / number_of_days_in_period('monthly', date(2016, 3, 31))  # noqa


def test_budgets_dateline_quarterly():
    BUDGET = Decimal(123456.7)
    budgets = get_budgets('2014-05-01 custom "budget" Expenses:Books "quarterly"  {} EUR'.format(BUDGET))  # noqa

    assert budgets.budget('Expenses:Books', date(2016, 2, 1), date(2016, 2, 2))['EUR'] == BUDGET / number_of_days_in_period('quarterly', date(2016, 2, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 5, 30), date(2016, 5, 31))['EUR'] == BUDGET / number_of_days_in_period('quarterly', date(2016, 5, 30))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 8, 15), date(2016, 8, 16))['EUR'] == BUDGET / number_of_days_in_period('quarterly', date(2016, 8, 15))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 11, 15), date(2016, 11, 16))['EUR'] == BUDGET / number_of_days_in_period('quarterly', date(2016, 11, 15))  # noqa


def test_budgets_dateline_yearly():
    BUDGET = Decimal(99999.87)
    budgets = get_budgets('2010-01-01 custom "budget" Expenses:Books "yearly"  {} EUR'.format(BUDGET))  # noqa

    assert budgets.budget('Expenses:Books', date(2011, 2, 1), date(2011, 2, 2))['EUR'] == BUDGET / number_of_days_in_period('yearly', date(2011, 2, 1))  # noqa
    assert budgets.budget('Expenses:Books', date(2015, 5, 30), date(2015, 5, 31))['EUR'] == BUDGET / number_of_days_in_period('yearly', date(2015, 5, 30))  # noqa
    assert budgets.budget('Expenses:Books', date(2016, 8, 15), date(2016, 8, 16))['EUR'] == BUDGET / number_of_days_in_period('yearly', date(2016, 8, 15))  # noqa


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
