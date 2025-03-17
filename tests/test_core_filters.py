from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from beancount.core.account import has_component
from beancount.core.data import Transaction

from fava.beans import create
from fava.beans.account import get_entry_accounts
from fava.core.filters import AccountFilter
from fava.core.filters import AdvancedFilter
from fava.core.filters import FilterError
from fava.core.filters import FilterSyntaxLexer
from fava.core.filters import Match
from fava.core.filters import MatchAmount
from fava.core.filters import TimeFilter

if TYPE_CHECKING:  # pragma: no cover
    from fava.core import FavaLedger


def test_match() -> None:
    assert Match("asdf")("asdf")
    assert Match("asdf")("asdfasdf")
    assert Match("asdf")("aasdfasdf")
    assert Match("^asdf")("asdfasdf")
    assert not Match("asdf")("fdsadfs")
    assert not Match("^asdf")("aasdfasdf")
    assert Match("(((")("(((")


def test_match_amount() -> None:
    one = Decimal(1)
    two = Decimal(2)

    one_amt = create.amount("1 EUR")
    two_amt = create.amount("2 EUR")
    three_amt = create.amount("3 EUR")

    assert MatchAmount("=", one)(one_amt)
    assert MatchAmount("=", one)(one_amt)

    assert MatchAmount(">", two)(three_amt)
    assert not MatchAmount(">", two)(two_amt)
    assert not MatchAmount(">", two)(one_amt)

    assert MatchAmount(">=", two)(three_amt)
    assert MatchAmount(">=", two)(two_amt)
    assert not MatchAmount(">=", two)(one_amt)

    assert not MatchAmount("<", two)(three_amt)
    assert not MatchAmount("<", two)(two_amt)
    assert MatchAmount("<", two)(one_amt)

    assert not MatchAmount("<=", two)(three_amt)
    assert MatchAmount("<=", two)(two_amt)
    assert MatchAmount("<=", two)(one_amt)


def test_lexer_basic() -> None:
    lex = FilterSyntaxLexer().lex
    data = "#some_tag ^some_link -^some_link"
    assert [(tok.type, tok.value) for tok in lex(data)] == [
        ("TAG", "some_tag"),
        ("LINK", "some_link"),
        ("-", "-"),
        ("LINK", "some_link"),
    ]
    data = "'string' string \"string\""
    assert [(tok.type, tok.value) for tok in lex(data)] == [
        ("STRING", "string"),
        ("STRING", "string"),
        ("STRING", "string"),
    ]
    with pytest.raises(FilterError):
        list(lex("|"))


def test_lexer_literals_in_string() -> None:
    lex = FilterSyntaxLexer().lex
    data = "string-2-2 string"
    assert [(tok.type, tok.value) for tok in lex(data)] == [
        ("STRING", "string-2-2"),
        ("STRING", "string"),
    ]


def test_lexer_key() -> None:
    lex = FilterSyntaxLexer().lex
    data = 'payee:asdfasdf ^some_link somekey:"testtest" units>80.2 '
    assert [(tok.type, tok.value) for tok in lex(data)] == [
        ("KEY", "payee"),
        ("EQ_OP", ":"),
        ("STRING", "asdfasdf"),
        ("LINK", "some_link"),
        ("KEY", "somekey"),
        ("EQ_OP", ":"),
        ("STRING", "testtest"),
        ("KEY", "units"),
        ("CMP_OP", ">"),
        ("NUMBER", Decimal("80.2")),
    ]


def test_lexer_parentheses() -> None:
    lex = FilterSyntaxLexer().lex
    data = "(payee:asdfasdf ^some_link) (somekey:'testtest')"
    assert [(tok.type, tok.value) for tok in lex(data)] == [
        ("(", "("),
        ("KEY", "payee"),
        ("EQ_OP", ":"),
        ("STRING", "asdfasdf"),
        ("LINK", "some_link"),
        (")", ")"),
        ("(", "("),
        ("KEY", "somekey"),
        ("EQ_OP", ":"),
        ("STRING", "testtest"),
        (")", ")"),
    ]


def test_filterexception() -> None:
    with pytest.raises(FilterError, match='Illegal character """ in filter'):
        AdvancedFilter('who:"fff')

    with pytest.raises(FilterError, match="Failed to parse filter"):
        AdvancedFilter('any(who:"Martin"')


TOTAL_ENTRIES = 1826
NON_TRANSACTION_ENTRIES = 893


@pytest.mark.parametrize(
    ("string", "number"),
    [
        ('any(account:"Assets:US:ETrade")', 48 + NON_TRANSACTION_ENTRIES),
        ('all(-account:"Assets:US:ETrade")', TOTAL_ENTRIES - 48),
        ("#test", 2 + NON_TRANSACTION_ENTRIES),
        ("#test,#nomatch", 2 + NON_TRANSACTION_ENTRIES),
        ("-#nomatch", TOTAL_ENTRIES),
        ("-#nomatch -#nomatch", TOTAL_ENTRIES),
        ("-#nomatch -#test", TOTAL_ENTRIES - 2),
        ("-#test", TOTAL_ENTRIES - 2),
        ("^test-link", 3 + NON_TRANSACTION_ENTRIES),
        ("^test-link,#test", 4 + NON_TRANSACTION_ENTRIES),
        ("^test-link -#test", 2 + NON_TRANSACTION_ENTRIES),
        ("payee:BayBook", 62 + NON_TRANSACTION_ENTRIES),
        ("BayBook", 62 + NON_TRANSACTION_ENTRIES),
        (
            "(payee:BayBook, #test,#nomatch) -#nomatch",
            64 + NON_TRANSACTION_ENTRIES,
        ),
        ('payee:"BayBo.*"', 62 + NON_TRANSACTION_ENTRIES),
        ('payee:"baybo.*"', 62 + NON_TRANSACTION_ENTRIES),
        (r'number:"\d*"', 2 + NON_TRANSACTION_ENTRIES),
        ('not_a_meta_key:".*"', 0 + NON_TRANSACTION_ENTRIES),
        ('any(overage:"GB$")', 1 + NON_TRANSACTION_ENTRIES),
        ("=26.87", 1 + NON_TRANSACTION_ENTRIES),
        (">=17500", 3 + NON_TRANSACTION_ENTRIES),
        (">=17500 <18000", 1 + NON_TRANSACTION_ENTRIES),
        ("any(units >= 17500)", 3 + NON_TRANSACTION_ENTRIES),
    ],
)
def test_advanced_filter(
    example_ledger: FavaLedger,
    string: str,
    number: int,
) -> None:
    filter_ = AdvancedFilter(string)
    filtered_entries = filter_.apply(example_ledger.all_entries)
    assert len(filtered_entries) == number


def test_null_meta_posting() -> None:
    filter_ = AdvancedFilter('any(some_meta:"1")')

    txn = create.transaction(
        {},
        datetime.date(2017, 12, 12),
        "*",
        "",
        "",
        frozenset(),
        frozenset(),
        [create.posting("Assets:ETrade:Cash", "100 USD")],
    )
    assert txn.postings[0].meta is None
    assert len(filter_.apply([txn])) == 0


def test_account_filter(example_ledger: FavaLedger) -> None:
    account_filter = AccountFilter("")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert filtered_entries is example_ledger.all_entries

    account_filter = AccountFilter("Assets")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 488 + NON_TRANSACTION_ENTRIES
    for entry in filtered_entries:
        assert any(
            has_component(a, "Assets") for a in get_entry_accounts(entry)
        ) or not isinstance(entry, Transaction)

    account_filter = AccountFilter(".*US:State")
    filtered_entries = account_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 64 + NON_TRANSACTION_ENTRIES


def test_time_filter(example_ledger: FavaLedger) -> None:
    time_filter = TimeFilter(
        example_ledger.options,
        example_ledger.fava_options,
        "2017",
    )

    date_range = time_filter.date_range
    assert date_range
    assert date_range.begin == datetime.date(2017, 1, 1)
    assert date_range.end == datetime.date(2018, 1, 1)
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert len(filtered_entries) == 83

    time_filter = TimeFilter(
        example_ledger.options,
        example_ledger.fava_options,
        "1000",
    )
    filtered_entries = time_filter.apply(example_ledger.all_entries)
    assert not filtered_entries

    with pytest.raises(FilterError):
        TimeFilter(
            example_ledger.options,
            example_ledger.fava_options,
            "no_date",
        )
