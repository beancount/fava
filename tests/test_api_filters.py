import datetime

from beancount.core import account
from beancount.core.data import Transaction
import pytest

from fava.api.filters import (
    FilterException, AccountFilter, FromFilter, PayeeFilter, TagFilter,
    TimeFilter)


def test_filterexception():
    with pytest.raises(FilterException) as exception:
        raise FilterException('type', 'error')
    exception = exception.value
    assert str(exception) == 'error'
    assert str(exception) == exception.message


def test_from_filter(example_api):
    filter = FromFilter()

    filter.set('has_account("Assets:US:ETrade")')
    filtered_entries = filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 53

    with pytest.raises(FilterException):
        filter.set('invalid')

    filter.set('')
    filtered_entries = filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == len(example_api.all_entries)


def test_account_filter(example_api):
    account_filter = AccountFilter()

    account_filter.set('Assets')
    filtered_entries = account_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 541
    assert all(map(
        lambda x: hasattr(x, 'account') and
        account.has_component(x.account, 'Assets') or any(map(
            lambda p: account.has_component(p.account, 'Assets'), x.postings)),
        filtered_entries))

    account_filter.set('.*US:State')
    filtered_entries = account_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 67


def test_time_filter(example_api):
    time_filter = TimeFilter()

    time_filter.set('2017')
    assert time_filter.begin_date == datetime.date(2017, 1, 1)
    assert time_filter.end_date == datetime.date(2018, 1, 1)
    filtered_entries = time_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 83

    time_filter.set('1000')
    filtered_entries = time_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == 0

    time_filter.set(None)
    filtered_entries = time_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == len(example_api.all_entries)

    with pytest.raises(FilterException):
        time_filter.set('no_date')


def test_tag_filter(example_api):
    tag_filter = TagFilter()

    tag_filter.set('test, ,')
    filtered_entries = tag_filter.apply(
        example_api.all_entries, example_api.options)
    assert all(map(
        lambda x: isinstance(x, Transaction),
        filtered_entries))
    assert len(filtered_entries) == 0

    assert tag_filter.set('')
    filtered_entries = tag_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == len(example_api.all_entries)


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

    payee_filter.set('')
    filtered_entries = payee_filter.apply(
        example_api.all_entries, example_api.options)
    assert len(filtered_entries) == len(example_api.all_entries)
