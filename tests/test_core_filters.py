# pylint: disable=missing-docstring
import datetime

import pytest
from beancount.core import account
from beancount.core.data import create_simple_posting
from beancount.core.data import Transaction

from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import FilterException
from fava.core.filters import FilterSyntaxLexer
from fava.core.filters import Match
from fava.core.filters import TimeFilter

LEX = FilterSyntaxLexer().lex


def test_match():
    assert Match("asdf")("asdf")
    assert Match("asdf")("asdfasdf")
    assert Match("asdf")("aasdfasdf")
    assert Match("^asdf")("asdfasdf")
    assert not Match("asdf")("fdsadfs")
    assert not Match("^asdf")("aasdfasdf")
    assert Match("(((")("(((")


def test_lexer_basic():
    data = "#some_tag ^some_link -^some_link"
    assert [(tok.type, tok.value) for tok in LEX(data)] == [
        ("TAG", "some_tag"),
        ("LINK", "some_link"),
        ("-", "-"),
        ("LINK", "some_link"),
    ]
    data = "'string' string \"string\""
    assert [(tok.type, tok.value) for tok in LEX(data)] == [
        ("STRING", "string"),
        ("STRING", "string"),
        ("STRING", "string"),
    ]
    with pytest.raises(FilterException):
        list(LEX("|"))


def test_lexer_literals_in_string():
    data = "string-2-2 string"
    assert [(tok.type, tok.value) for tok in LEX(data)] == [
        ("STRING", "string-2-2"),
        ("STRING", "string"),
    ]


def test_lexer_key():
    data = 'payee:asdfasdf ^some_link somekey:"testtest" '
    assert [(tok.type, tok.value) for tok in LEX(data)] == [
        ("KEY", "payee"),
        ("STRING", "asdfasdf"),
        ("LINK", "some_link"),
        ("KEY", "somekey"),
        ("STRING", "testtest"),
    ]


def test_lexer_parentheses():
    data = "(payee:asdfasdf ^some_link) (somekey:'testtest')"
    assert [(tok.type, tok.value) for tok in LEX(data)] == [
        ("(", "("),
        ("KEY", "payee"),
        ("STRING", "asdfasdf"),
        ("LINK", "some_link"),
        (")", ")"),
        ("(", "("),
        ("KEY", "somekey"),
        ("STRING", "testtest"),
        (")", ")"),
    ]


FILTER = AdvancedFilter({}, {})


def test_filterexception():
    with pytest.raises(FilterException) as exception:
        raise FilterException("type", "error")
    exception = exception.value
    assert str(exception) == "error"
    assert str(exception) == exception.message

    with pytest.raises(FilterException):
        FILTER.set('who:"fff')
        assert str(exception) == 'Illegal character """ in filter: who:"fff'

    with pytest.raises(FilterException):
        FILTER.set('any(who:"Martin"')
        assert str(exception) == 'Failed to parse filter: any(who:"Martin"'


@pytest.mark.parametrize(
    "string,number",
    [
        ('any(account:"Assets:US:ETrade")', 48),
        ('all(-account:"Assets:US:ETrade")', 1826 - 48),
        ("#test", 2),
        ("#test,#nomatch", 2),
        ("-#nomatch", 1826),
        ("-#nomatch -#nomatch", 1826),
        ("-#nomatch -#test", 1824),
        ("-#test", 1824),
        ("^test-link", 3),
        ("^test-link,#test", 4),
        ("^test-link -#test", 2),
        ("payee:BayBook", 62),
        ("BayBook", 62),
        ("(payee:BayBook, #test,#nomatch) -#nomatch", 64),
        ('payee:"BayBo.*"', 62),
        ('payee:"baybo.*"', 62),
        (r'number:"\d*"', 3),
        ('not_a_meta_key:".*"', 0),
        ('name:".*ETF"', 4),
        ('name:".*ETF$"', 3),
        ('name:".*etf"', 4),
        ('name:".*etf$"', 3),
        ('any(overage:"GB$")', 1),
    ],
)
def test_advanced_filter(example_ledger, string, number):
    FILTER.set(string)
    filtered_entries = FILTER.apply(example_ledger.all_entries)
    assert len(filtered_entries) == number


def test_null_meta_posting():
    FILTER.set('any(some_meta:"1")')

    txn = Transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "",
        "",
        None,
        None,
        [],
    )
    # This will create a posting with meta set to `None`.
    create_simple_posting(txn, "Assets:ETrade:Cash", "100", "USD")
    assert txn.postings[0].meta is None
    assert len(FILTER.apply([txn])) == 0


def test_account_filter(example_ledger):
    account_filter = AccountFilter(
        example_ledger.options, example_ledger.fava_options
    )

    account_filter.set("Assets")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 541
    assert all(
        map(
            lambda x: hasattr(x, "account")
            and account.has_component(x.account, "Assets")
            or any(
                map(
                    lambda p: account.has_component(p.account, "Assets"),
                    x.postings,
                )
            ),
            filtered_entries,
        )
    )

    account_filter.set(".*US:State")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 67


def test_time_filter(example_ledger):
    time_filter = TimeFilter(
        example_ledger.options, example_ledger.fava_options
    )

    time_filter.set("2017")
    assert time_filter.begin_date == datetime.date(2017, 1, 1)
    assert time_filter.end_date == datetime.date(2018, 1, 1)
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 83

    time_filter.set("1000")
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert not filtered_entries

    time_filter.set(None)
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == len(example_ledger.all_entries)

    with pytest.raises(FilterException):
        time_filter.set("no_date")
