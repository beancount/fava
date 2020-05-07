# pylint: disable=missing-docstring
import re
from datetime import date
from pathlib import Path
from textwrap import dedent

import pytest
from beancount.core.amount import A
from beancount.core.data import Posting
from beancount.core.data import Transaction

from fava.core import FavaLedger
from fava.core.fava_options import InsertEntryOption
from fava.core.file import find_entry_lines
from fava.core.file import get_entry_slice
from fava.core.file import insert_entry
from fava.core.file import insert_metadata_in_file
from fava.core.file import leading_space
from fava.core.file import next_key
from fava.core.file import save_entry_slice
from fava.helpers import FavaAPIException


def test_get_entry_slice(example_ledger) -> None:
    entry = example_ledger.get_entry("d4a067d229bfda57c8c984d1615da699")
    assert get_entry_slice(entry) == (
        """2016-05-03 * "Chichipotle" "Eating out with Joe"
  Liabilities:US:Chase:Slate                       -21.70 USD
  Expenses:Food:Restaurant                          21.70 USD""",
        "d60da810c0c7b8a57ae16be409c5e17a640a837c1ac29719ebe9f43930463477",
    )


def test_save_entry_slice(example_ledger) -> None:
    entry = example_ledger.get_entry("d4a067d229bfda57c8c984d1615da699")

    entry_source, sha256sum = get_entry_slice(entry)
    new_source = """2016-05-03 * "Chichipotle" "Eating out with Joe"
  Expenses:Food:Restaurant                          21.70 USD"""
    filename = Path(entry.meta["filename"])
    contents = filename.read_text("utf-8")

    with pytest.raises(FavaAPIException):
        save_entry_slice(entry, new_source, "wrong hash")
        assert filename.read_text("utf-8") == contents

    new_sha256sum = save_entry_slice(entry, new_source, sha256sum)
    assert filename.read_text("utf-8") != contents
    sha256sum = save_entry_slice(entry, entry_source, new_sha256sum)
    assert filename.read_text("utf-8") == contents


def test_next_key() -> None:
    assert next_key("statement", {}) == "statement"
    assert next_key("statement", {"foo": 1}) == "statement"
    assert next_key("statement", {"foo": 1, "statement": 1}) == "statement-2"
    assert (
        next_key("statement", {"statement": 1, "statement-2": 1})
        == "statement-3"
    )


def test_leading_space() -> None:
    assert leading_space("test") == "  "
    assert leading_space("	test") == "	"
    assert leading_space("  test") == "  "
    assert leading_space('    2016-10-31 * "Test" "Test"') == "    "
    assert leading_space("\r\t\r\ttest") == "\r\t\r\t"
    assert leading_space("\ntest") == "\n"


def test_insert_metadata_in_file(tmp_path) -> None:
    file_content = dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """
    )
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    # Insert some metadata lines.
    insert_metadata_in_file(str(samplefile), 1, "metadata", "test1")
    insert_metadata_in_file(str(samplefile), 1, "metadata", "test2")
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test2"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """
    )

    # Check that inserting also works if the next line is empty.
    insert_metadata_in_file(str(samplefile), 5, "metadata", "test1")
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test2"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
          metadata: "test1"
        """
    )


def test_find_entry_lines() -> None:
    file_content = dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-02-26 note Accounts:Text "Uncle Boons"
        2016-02-26 note Accounts:Text "Uncle Boons"
        ; test
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """
    )
    lines = file_content.split("\n")
    entry_lines = [
        '2016-02-26 * "Uncle Boons" "Eating out alone"',
        "    Liabilities:US:Chase:Slate                       -24.84 USD",
        "    Expenses:Food:Restaurant                          24.84 USD",
    ]
    note_line = ['2016-02-26 note Accounts:Text "Uncle Boons"']
    assert find_entry_lines(lines, 0) == entry_lines
    assert find_entry_lines(lines, 7) == entry_lines
    assert find_entry_lines(lines, 4) == note_line
    assert find_entry_lines(lines, 5) == note_line


def test_insert_entry_transaction(tmp_path) -> None:
    file_content = dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """
    )
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    postings = [
        Posting(
            "Liabilities:US:Chase:Slate",
            A("-10.00 USD"),
            None,
            None,
            None,
            None,
        ),
        Posting("Expenses:Food", A("10.00 USD"), None, None, None, None),
    ]

    transaction = Transaction(
        {}, date(2016, 1, 1), "*", "new payee", "narr", None, None, postings,
    )

    # Test insertion without "insert-entry" options.
    insert_entry(transaction, str(samplefile), [], 61)
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD
        """
    )

    # Verify that InsertEntryOptions with dates greater or equal than the
    # transaction dates are ignored.
    options = [
        InsertEntryOption(
            date(2015, 1, 1), re.compile(".*:Food"), str(samplefile), 1,
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(".*:FOOO"), str(samplefile), 1,
        ),
        InsertEntryOption(
            date(2017, 1, 1), re.compile(".*:Food"), str(samplefile), 6,
        ),
    ]
    new_options = insert_entry(
        transaction._replace(narration="narr1"), str(samplefile), options, 61
    )
    assert new_options[0].lineno == 5
    assert new_options[1].lineno == 5
    assert new_options[2].lineno == 10
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-01-01 * "new payee" "narr1"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD
        """
    )

    # Verify that previous postings are matched against InsertEntryOptions when
    # the last posting doesn't match.
    options = [
        InsertEntryOption(
            date(2015, 1, 1), re.compile(".*:Slate"), str(samplefile), 5,
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(".*:FOOO"), str(samplefile), 1,
        ),
    ]
    transaction = transaction._replace(narration="narr2")
    new_options = insert_entry(transaction, str(samplefile), options, 61)
    assert new_options[0].lineno == 9
    assert new_options[1].lineno == 1
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-01-01 * "new payee" "narr1"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-01-01 * "new payee" "narr2"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD
        """
    )

    # Verify that preference is given to InsertEntryOptions with later dates in
    # case several of them match a posting.
    options = [
        InsertEntryOption(
            date(2015, 1, 1), re.compile(".*:Food"), str(samplefile), 5,
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(".*:Food"), str(samplefile), 1,
        ),
    ]
    transaction = transaction._replace(narration="narr3")
    insert_entry(transaction, str(samplefile), options, 61)
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-01-01 * "new payee" "narr3"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-01-01 * "new payee" "narr1"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-01-01 * "new payee" "narr2"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD
        """
    )


def test_insert_entry_align(tmp_path) -> None:
    file_content = dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """
    )
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    postings = [
        Posting(
            "Liabilities:US:Chase:Slate",
            A("-10.00 USD"),
            None,
            None,
            None,
            None,
        ),
        Posting("Expenses:Food", A("10.00 USD"), None, None, None, None,),
    ]

    transaction = Transaction(
        {}, date(2016, 1, 1), "*", "new payee", "narr", None, None, postings,
    )

    insert_entry(transaction, str(samplefile), [], 50)
    assert samplefile.read_text("utf-8") == dedent(
        """\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate              -10.00 USD
          Expenses:Food                            10.00 USD
        """
    )


def test_render_entries(example_ledger: FavaLedger, snapshot) -> None:
    entry1 = example_ledger.get_entry("4af0865b1371c1b5576e9ff7f7d20dc9")
    entry2 = example_ledger.get_entry("85f3ba57bf52dc1bd6c77ef3510223ae")
    postings = [
        Posting("Expenses:Food", A("10.00 USD"), None, None, None, None),
    ]
    transaction = Transaction(
        {}, date(2016, 1, 1), "*", "new payee", "narr", None, None, postings,
    )
    entries = example_ledger.file.render_entries([entry1, entry2, transaction])
    snapshot("\n".join(entries))

    file_content = dedent(
        """\
        2016-04-09 * "Uncle Boons" "" #trip-new-york-2016
          Liabilities:US:Chase:Slate                       -52.22 USD
          Expenses:Food:Restaurant                          52.22 USD

        2016-05-04 * "BANK FEES" "Monthly bank fee"
          Assets:US:BofA:Checking                           -4.00 USD
          Expenses:Financial:Fees                            4.00 USD
        """
    )

    assert file_content == "\n".join(
        example_ledger.file.render_entries([entry1, entry2])
    )
