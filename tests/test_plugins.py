# pylint: disable=missing-docstring

from textwrap import dedent
import os

from beancount.loader import load_file, load_string

from fava.plugins.link_documents import DocumentError


def _format(string, args):
    """Dedent, and format (escaping backslashes in paths for Windows)."""
    args = (str(path).replace("\\", "\\\\") for path in args)
    return dedent(string).format(*args)


def test_plugins(tmpdir):
    # pylint: disable=too-many-locals
    sample_folder = tmpdir.mkdir("fava_plugins")

    documents_folder = sample_folder.mkdir("documents")

    foo_folder = documents_folder.mkdir("Expenses").mkdir("Foo")
    sample_statement1 = foo_folder.join("2016-11-01 Test 1.pdf")
    sample_statement1.write("Hello World 1")
    sample_statement1_short = os.path.join(
        "documents", "Expenses", "Foo", "2016-11-01 Test 1.pdf"
    )
    sample_statement2 = foo_folder.join("2016-11-01 Test 2.pdf")
    sample_statement2.write("Hello World 2")
    sample_statement3 = foo_folder.join("2016-11-01 Test 3 discovered.pdf")
    sample_statement3.write("Hello World 3")

    assets_folder = documents_folder.mkdir("Assets").mkdir("Cash")
    sample_statement4 = assets_folder.join("2016-11-01 Test 4.pdf")
    sample_statement4_short = os.path.join(
        "documents", "Assets", "Cash", "2016-11-01 Test 4.pdf"
    )
    sample_statement4.write("Hello World 4")
    sample_statement5 = assets_folder.join("Test 5.pdf")
    sample_statement5_short = os.path.join(
        "documents", "Assets", "Cash", "Test 5.pdf"
    )
    sample_statement5.write("Hello World 5")

    beancount_file = sample_folder.join("example.beancount")
    beancount_file.write(
        _format(
            """
        option "title" "Test"
        option "operating_currency" "EUR"
        option "documents" "{}"

        plugin "fava.plugins.link_documents"
        plugin "fava.plugins.tag_discovered_documents"

        2016-10-31 open Expenses:Foo
        2016-10-31 open Assets:Cash

        2016-11-01 * "Foo" "Bar"
            document: "{}"
            Expenses:Foo                100 EUR
            Assets:Cash

        2016-11-02 * "Foo" "Bar"
            document: "{}"
            document-2: "{}"
            Expenses:Foo        100 EUR
            Assets:Cash

        2016-11-02 document Assets:Cash "{}"
    """,
            (
                documents_folder,
                sample_statement2,
                sample_statement1_short,
                sample_statement4_short,
                sample_statement5_short,
            ),
        )
    )

    entries, errors, _ = load_file(str(beancount_file))

    assert not errors
    assert len(entries) == 9

    assert "linked" in entries[3].tags
    assert "linked" in entries[4].tags
    assert "linked" in entries[5].tags

    assert entries[2].links == entries[5].links
    assert entries[7].links == entries[3].links == entries[4].links

    assert "discovered" in entries[6].tags
    assert not entries[8].tags


def test_link_documents_error(load_doc):
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


def test_link_documents_missing(tmpdir):
    sample_folder = tmpdir.mkdir("fava_plugins").mkdir("documents")

    bfile = _format(
        """
        option "documents" "{}"
        plugin "fava.plugins.link_documents"

        2016-10-31 open Expenses:Foo
        2016-10-31 open Assets:Cash

        2016-11-01 * "Foo" "Bar"
            document: "{}"
            Expenses:Foo                100 EUR
            Assets:Cash
    """,
        (sample_folder, os.path.join("test", "Foobar.pdf")),
    )

    entries, errors, _ = load_string(bfile)

    assert len(errors) == 1
    assert isinstance(errors[0], DocumentError)
    assert len(entries) == 3
