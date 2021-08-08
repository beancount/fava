# pylint: disable=missing-docstring
from pathlib import Path
from textwrap import dedent

from beancount.loader import load_file
from beancount.loader import load_string

from fava.plugins.link_documents import DocumentError


def test_plugins(tmp_path: Path) -> None:
    # Create sample files
    expenses_foo = tmp_path / "documents" / "Expenses" / "Foo"
    expenses_foo.mkdir(parents=True)
    (expenses_foo / "2016-11-02 Test 1.pdf").touch()
    (expenses_foo / "2016-11-03 Test 2.pdf").touch()
    (expenses_foo / "2016-11-04 Test 3 discovered.pdf").touch()
    assets_cash = tmp_path / "documents" / "Assets" / "Cash"
    assets_cash.mkdir(parents=True)
    (assets_cash / "2016-11-05 Test 4.pdf").touch()
    (assets_cash / "Test 5.pdf").touch()

    expenses_foo_rel = Path("documents") / "Expenses" / "Foo"
    assets_cash_rel = Path("documents") / "Assets" / "Cash"

    beancount_file = tmp_path / "example.beancount"
    beancount_file.write_text(
        dedent(
            f"""
        option "title" "Test"
        option "operating_currency" "EUR"
        option "documents" "{tmp_path / "documents"}"

        plugin "fava.plugins.link_documents"

        2016-10-30 open Expenses:Foo
        2016-10-31 open Assets:Cash

        2016-11-01 * "Foo" "Bar"
            document: "{expenses_foo / "2016-11-03 Test 2.pdf"}"
            document-2: "{assets_cash_rel / "2016-11-05 Test 4.pdf"}"
            Expenses:Foo                100 EUR
            Assets:Cash

        2016-11-07 * "Foo" "Bar"
            document: "{expenses_foo_rel / "2016-11-02 Test 1.pdf"}"
            document-2: "{assets_cash_rel / "2016-11-05 Test 4.pdf"}"
            Expenses:Foo        100 EUR
            Assets:Cash

        2016-11-06 document Assets:Cash "{assets_cash_rel / "Test 5.pdf"}"
        2017-11-06 balance Assets:Cash   -200 EUR
            document: "{assets_cash_rel / "Test 5.pdf"}"
        """.replace(
                "\\", "\\\\"
            )
        )
    )

    entries, errors, _ = load_file(str(beancount_file))

    assert not errors
    assert len(entries) == 10

    assert "linked" in entries[3].tags
    assert "linked" in entries[4].tags

    # Document can be linked twice
    assert len(entries[6].links) == 2
    assert entries[2].links == entries[4].links
    assert entries[8].links == entries[3].links


def test_link_documents_error(load_doc) -> None:
    """
    plugin "fava.plugins.link_documents"

    2016-10-31 open Expenses:Foo
    2016-10-31 open Assets:Cash

    2016-11-01 * "Foo" "Bar"
        document: "asdf"
        Expenses:Foo                100 EUR
        Assets:Cash
    """
    entries, errors, _ = load_doc

    assert len(errors) == 1
    assert len(entries) == 3


def test_link_documents_missing(tmp_path: Path) -> None:
    bfile = dedent(
        f"""
        option "documents" "{tmp_path}"
        plugin "fava.plugins.link_documents"

        2016-10-31 open Expenses:Foo
        2016-10-31 open Assets:Cash

        2016-11-01 * "Foo" "Bar"
            document: "{Path("test") / "Foobar.pdf"}"
            Expenses:Foo                100 EUR
            Assets:Cash
        """.replace(
            "\\", "\\\\"
        )
    )

    entries, errors, _ = load_string(bfile)

    assert len(errors) == 1
    assert isinstance(errors[0], DocumentError)
    assert len(entries) == 3
