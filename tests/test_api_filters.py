import datetime

from beancount.core import account
from beancount.core.data import Transaction
from fava.api.filters import AccountFilter, DateFilter, PayeeFilter, TagFilter


def test_account_filter(example_api):
    account_filter = AccountFilter()

    account_filter.set('Assets')
    filtered_entries = account_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 537
    assert all(map(
        lambda x: hasattr(x, 'account') and
        account.has_component(x.account, 'Assets') or any(map(
            lambda p: account.has_component(p.account, 'Assets'), x.postings)),
        filtered_entries))


def test_date_filter(example_api):
    date_filter = DateFilter()

    date_filter.set('2017')
    assert date_filter.begin_date == datetime.date(2017, 1, 1)
    assert date_filter.end_date == datetime.date(2018, 1, 1)
    filtered_entries = date_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 81

    date_filter.set('1000')
    filtered_entries = date_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 0

    date_filter.set(None)
    filtered_entries = date_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == len(example_api.all_entries)


def test_tag_filter(example_api):
    tag_filter = TagFilter()

    tag_filter.set('test')
    filtered_entries = tag_filter.apply(
        example_api.all_entries, example_api.options)
    assert all(map(
        lambda x: isinstance(x, Transaction),
        filtered_entries))
    assert len(filtered_entries) == 0


def test_payee_filter(example_api):
    payee_filter = PayeeFilter()

    payee_filter.set('BayBook')
    filtered_entries = payee_filter.apply(
        example_api.all_entries, example_api.options)
    assert all(map(
        lambda x: isinstance(x, Transaction),
        filtered_entries))
    assert len(filtered_entries) == 62

    payee_filter.set('asdfasdfasdf, BayBook')
    filtered_entries = payee_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 62

    payee_filter.set('asdfasdfasdvba')
    filtered_entries = payee_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 0
